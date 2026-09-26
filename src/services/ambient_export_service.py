"""Ambient World Packaging and Export Utilities.

Handles long-play stretching, teaser short extraction, localized metadata, and topic memory indexing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import subprocess
import imageio_ffmpeg

from src.core.telemetry import logger
from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def _probe_clip_duration(clip_path: Path) -> float:
    """Probe the exact duration of a video clip in seconds."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 5.0


def assemble_4k_master(video_clips: list[Path], audio_path: Optional[Path], out_master: Path, scene_hold_sec: float = 60.0, crf: int = 22) -> Path:
    """Assemble relaxing 4K master with 60.0s (1 full minute) Extended Perspective Hold per shot and slow 2.0s crossfades in CRF 22 format."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    n = len(video_clips)
    x_dur = 2.0  # Slow, meditative 2-second cross-dissolve
    
    if n == 1:
        if audio_path and audio_path.is_file():
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-i", str(audio_path), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        else:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]
    else:
        # Multi-Shot: Hold each scene for 60.0 seconds before slow 2.0s cross-dissolve
        inputs = []
        for c in video_clips:
            inputs.extend(["-stream_loop", "-1", "-t", str(scene_hold_sec), "-i", str(c)])
        
        if audio_path and audio_path.is_file():
            inputs.extend(["-i", str(audio_path)])
            scales = [f"[{i}:v]scale=3840:2160,setsar=1[s{i}]" for i in range(n)]
            filter_parts = list(scales)
            prev_tag = "s0"
            curr_offset = scene_hold_sec - x_dur
            for i in range(1, n):
                out_tag = f"v{i}" if i < n - 1 else "v"
                filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_tag}]")
                prev_tag = out_tag
                curr_offset += scene_hold_sec - x_dur
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        else:
            # Native Audio Mode (--no-bgm): Loop native video audio and acrossfade
            scales = [f"[{i}:v]scale=3840:2160,setsar=1[s{i}]" for i in range(n)]
            filter_v, filter_a = list(scales), []
            prev_v, prev_a = "s0", "0:a"
            curr_offset = scene_hold_sec - x_dur
            for i in range(1, n):
                out_v = f"v{i}" if i < n - 1 else "v"
                out_a = f"a{i}" if i < n - 1 else "a"
                filter_v.append(f"[{prev_v}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_v}]")
                filter_a.append(f"[{prev_a}][{i}:a]acrossfade=d={x_dur:.2f}[{out_a}]")
                prev_v = out_v
                prev_a = out_a
                curr_offset += scene_hold_sec - x_dur
            full_filter = ";".join(filter_v + filter_a)
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", full_filter, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        logger.error(f"failed_to_assemble_4k_master: {err}")
        raise

    return out_master


def assemble_dual_masters(video_clips: list[Path], audio_path: Optional[Path], ep_dir: Path, crf: int = 22) -> Dict[str, Path]:
    """Assemble 4K masters in CRF 22 format. If audio_path is provided, assembles BOTH Music Master and Pure Nature Master.
    If audio_path is None (--no-bgm), assembles ONLY a single Pure Nature Master.
    """
    master_music = ep_dir / "master_4k_ambient.mp4"
    if not master_music.is_file() or master_music.stat().st_size < 1000:
        if audio_path and audio_path.is_file():
            print(f"[STAGE 2 - MASTER ASSEMBLY] Assembling Music Master (With BGM, CRF {crf}) -> {master_music.name}")
            assemble_4k_master(video_clips, audio_path, master_music, crf=crf)
        else:
            print(f"[STAGE 2 - MASTER ASSEMBLY] Assembling Single Native Master (--no-bgm, CRF {crf}) -> {master_music.name}")
            assemble_4k_master(video_clips, None, master_music, crf=crf)
    else:
        logger.info(f"decision_master_video_cache_hit: Reusing {master_music.name} ($0.00 spend)")
        print(f"[DECISION - MASTER VIDEO CACHE HIT] Master 4K video already exists ({master_music.name}). Reusing asset ($0.00 spend).")

    # If specifically --no-bgm (audio_path is None), only produce the single master above
    if not audio_path:
        return {
            "music_master": master_music,
            "nature_master": None,
        }

    # Otherwise assemble dual version: Pure Nature Master (No Music)
    master_nature = ep_dir / "master_4k_ambient_nature_only.mp4"
    if not master_nature.is_file() or master_nature.stat().st_size < 1000:
        print(f"[STAGE 2 - DUAL MASTER ASSEMBLY] Assembling Pure Nature Master (No Music, CRF {crf}) -> {master_nature.name}")
        assemble_4k_master(video_clips, None, master_nature, crf=crf)
    else:
        logger.info(f"decision_nature_master_cache_hit: Reusing {master_nature.name} ($0.00 spend)")
        print(f"[DECISION - NATURE MASTER CACHE HIT] Pure Nature 4K video already exists ({master_nature.name}). Reusing asset ($0.00 spend).")

    return {
        "music_master": master_music,

        "nature_master": master_nature,
    }


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float]) -> Optional[Path]:
    """Export long-play multi-hour stream loop for all existing master versions (with BGM and pure nature)."""
    if not hours or hours <= 0:
        return None
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    label = int(hours) if hours.is_integer() else hours
    
    # 1. Stretch standard / music master
    lp_path = ep_dir / f"master_4k_{label}hour{suffix}_sleep.mp4"
    if master.is_file() and (not lp_path.is_file() or lp_path.stat().st_size < 1000):
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=hours * 3600.0, fade_to_black_hours=fade_hours)
    
    # 2. Automatically stretch pure nature / no-bgm master if it exists
    nature_master = ep_dir / "master_4k_ambient_nature_only.mp4"
    if nature_master.is_file() and nature_master.resolve() != master.resolve():
        lp_nature_path = ep_dir / f"master_4k_{label}hour_nature_only{suffix}_sleep.mp4"
        if not lp_nature_path.is_file() or lp_nature_path.stat().st_size < 1000:
            logger.info(f"stretching_dual_nature_master: {lp_nature_path.name}")
            print(f"[STAGE 3 - DUAL LONG-PLAY STRETCH] Stretching Pure Nature Master (No Music) -> {lp_nature_path.name}")
            export_long_play_broadcast(source_4k_video=nature_master, output_long_play=lp_nature_path, target_duration_seconds=hours * 3600.0, fade_to_black_hours=fade_hours)

    return lp_path


def handle_short_export(master: Path, ep_dir: Path, gen: bool) -> Optional[Path]:
    """Generate 9:16 vertical teaser short from 4K master."""
    if not gen:
        return None
    s_path = ep_dir / "short_9x16_teaser.mp4"
    if not s_path.is_file() or s_path.stat().st_size < 1000:
        generate_ambient_short(source_4k_video=master, output_short_path=s_path)
    return s_path


def export_metadata_packages(
    sb: AmbientStoryboard, ep_dir: Path, hours: Optional[float], fade_h: Optional[float]
) -> Tuple[YouTubeAmbientPackage, ThumbnailABPackage, Dict[str, LocalizedMetadata]]:
    """Generate YouTube packaging for both Music and Nature-Only variants, A/B thumbnails, and multi-language SEO."""
    pkg_music = generate_youtube_ambient_package(sb.primary_archetype, hours or 1.0, sb.secondary_archetype, fade_h)
    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg_music.model_dump(), indent=2), encoding="utf-8")
    
    # Generate dedicated Nature-Only metadata package for dual-upload
    pkg_nature = generate_youtube_ambient_package(sb.primary_archetype, hours or 1.0, sb.secondary_archetype, fade_h)
    pkg_nature.title = f"{pkg_nature.title} | Pure Nature Sounds (NO MUSIC) [4K ASMR]"
    pkg_nature.description = f"100% pure natural ambient soundscape without background music.\n\n{pkg_nature.description}"
    (ep_dir / "youtube_packaging_nature_only.json").write_text(json.dumps(pkg_nature.model_dump(), indent=2), encoding="utf-8")

    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg_music.title, pkg_music.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2), encoding="utf-8")
    return pkg_music, ab, loc
