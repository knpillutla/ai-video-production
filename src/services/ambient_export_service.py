"""Ambient World Packaging and Export Utilities.

Handles long-play stretching, teaser short extraction, localized metadata, and topic memory indexing.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import subprocess
import imageio_ffmpeg

from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory
from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def assemble_4k_master(video_clips: list[Path], audio_path: Optional[Path], out_master: Path) -> Path:
    """Assemble seamless 4K master video with smooth cross-dissolve transitions and capped 4-thread CPU usage."""
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    n = len(video_clips)
    
    if audio_path and audio_path.is_file():
        if n == 1:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-i", str(audio_path), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        elif n == 2:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-i", str(video_clips[1]), "-i", str(audio_path), "-filter_complex", "[0:v][1:v]xfade=transition=fade:duration=1.5:offset=28.5[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
        else:
            inputs = []
            for c in video_clips:
                inputs.extend(["-i", str(c)])
            inputs.extend(["-i", str(audio_path)])
            filter_parts, prev_tag, curr_offset = [], "0:v", 28.5
            for i in range(1, n):
                out_tag = f"v{i}" if i < n - 1 else "v"
                filter_parts.append(f"[{prev_tag}][{i}:v]xfade=transition=fade:duration=1.5:offset={curr_offset:.1f}[{out_tag}]")
                prev_tag = out_tag
                curr_offset += 28.5
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out_master)]
    else:
        # Native audio mode (--no-bgm): use sound embedded directly in video clips
        if n == 1:
            cmd = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-c", "copy", "-movflags", "+faststart", str(out_master)]
        else:
            inputs = []
            for c in video_clips:
                inputs.extend(["-i", str(c)])
            filter_v, filter_a = [], []
            prev_v, prev_a, curr_offset = "0:v", "0:a", 28.5
            for i in range(1, n):
                out_v = f"v{i}" if i < n - 1 else "v"
                out_a = f"a{i}" if i < n - 1 else "a"
                filter_v.append(f"[{prev_v}][{i}:v]xfade=transition=fade:duration=1.5:offset={curr_offset:.1f}[{out_v}]")
                filter_a.append(f"[{prev_a}][{i}:a]acrossfade=d=1.5[{out_a}]")
                prev_v = out_v
                prev_a = out_a
                curr_offset += 28.5
            full_filter = ";".join(filter_v + filter_a)
            cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", full_filter, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError:
        # Fallback if audio track is missing in some video clips
        if n == 1:
            cmd_fb = [ffmpeg_bin, "-y", "-i", str(video_clips[0]), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-movflags", "+faststart", str(out_master)]
        else:
            filter_parts, prev_tag, curr_offset = [], "0:v", 28.5
            for i in range(1, n):
                out_tag = f"v{i}" if i < n - 1 else "v"
                filter_parts.append(f"[{prev_tag}][{i}:v]xfade=transition=fade:duration=1.5:offset={curr_offset:.1f}[{out_tag}]")
                prev_tag = out_tag
                curr_offset += 28.5
            cmd_fb = [ffmpeg_bin, "-y", *[arg for c in video_clips for arg in ("-i", str(c))], "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", "18", "-movflags", "+faststart", str(out_master)]
        subprocess.run(cmd_fb, capture_output=True, check=True)

    return out_master


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float]) -> Optional[Path]:
    """Export long-play multi-hour stream loop with optional fade to black."""
    if not hours or hours <= 0:
        return None
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    label = int(hours) if hours.is_integer() else hours
    lp_path = ep_dir / f"master_4k_{label}hour{suffix}_sleep.mp4"
    if not lp_path.is_file() or lp_path.stat().st_size < 1000:
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=hours * 3600.0, fade_to_black_hours=fade_hours)
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
    """Generate YouTube packaging, A/B thumbnails, multi-language SEO, and persist in Topic Memory."""
    pkg = generate_youtube_ambient_package(sb.primary_archetype, hours or 1.0, sb.secondary_archetype, fade_h)
    (ep_dir / "youtube_packaging.json").write_text(json.dumps(pkg.model_dump(), indent=2), encoding="utf-8")
    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg.title, pkg.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2), encoding="utf-8")
    topic_memory.remember_topic(sb.title, f"ambient_{sb.cluster}", [sb.primary_archetype, sb.cluster, "relaxation", "sleep", "4k", "432hz"], f"Velvet Ambient: {sb.title}", ep_dir.name)
    return pkg, ab, loc
