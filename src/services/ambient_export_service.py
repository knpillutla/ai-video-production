from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path
from typing import Dict, Optional, Tuple, TYPE_CHECKING
import imageio_ffmpeg

from src.core.telemetry import logger
from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.cineloop_service import build_seamless_forward_cineloop, get_media_duration
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

if TYPE_CHECKING:
    from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def probe_clip_geometry(clip_path: Path) -> Tuple[int, int]:
    """Probe the exact width and height of an input clip."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore", creationflags=_SUBPROCESS_FLAGS)
        m = re.search(r",\s*(\d{3,4})x(\d{3,4})", res.stderr)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return 1920, 1080


def build_adaptive_resolution_filter(clip_path: Path, target_w: int = 3840, target_h: int = 2160, target_fps: int = 24) -> str:
    """Build a resolution- and fps-aware video filter: enforces target_fps, native 4K scaling, and safe aspect ratio."""
    w, h = probe_clip_geometry(clip_path)
    fps_f = f"fps={target_fps},"
    if w == target_w and h == target_h:
        return f"{fps_f}setsar=1"
    target_aspect = target_w / target_h
    clip_aspect = (w / h) if h > 0 else target_aspect
    if abs(clip_aspect - target_aspect) < 0.01:
        return f"{fps_f}scale={target_w}:{target_h}:flags=lanczos,setsar=1"
    return f"{fps_f}scale={target_w}:{target_h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1"


def assemble_4k_master(video_clips: list[Path], audio_path: Optional[Path], out_master: Path, scene_hold_sec: float = 60.0, crf: int = 22, target_duration_sec: Optional[float] = None, is_narration: bool = False, **kwargs) -> Path:
    """Assemble relaxing 4K master with seamless forward cineloops and crossfades in CRF 22 format."""
    from src.services.procedural_foley import synthesize_foley_stem
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    n, x_dur = len(seamless_clips), 2.0
    target_audio = audio_path
    if not target_audio or not target_audio.is_file():
        has_clip_audio = all("Audio:" in subprocess.run([ffmpeg_bin, "-i", str(c)], capture_output=True, text=True, errors="ignore", creationflags=_SUBPROCESS_FLAGS).stderr for c in seamless_clips)
        if not has_clip_audio:
            foley_wav = out_master.parent / "procedural_nature_foley.wav"
            if not foley_wav.is_file() or foley_wav.stat().st_size < 1000:
                synthesize_foley_stem(weather_type="water stream alpine breeze", setting_type="nature", space="outdoor", duration_seconds=scene_hold_sec + 5.0, output_path=foley_wav)
            target_audio = foley_wav

    if target_duration_sec and float(target_duration_sec) > 0:
        eff_master_dur = float(target_duration_sec)
    else:
        a_dur = get_media_duration(target_audio) if (target_audio and target_audio.is_file()) else 0.0
        eff_master_dur = max(a_dur, float(scene_hold_sec or 60.0)) if a_dur > 15.0 else (float(scene_hold_sec) if (scene_hold_sec and scene_hold_sec > 0) else 60.0)

    is_speech = is_narration or "narrat" in str(target_audio).lower() or kwargs.get("is_narration", False)
    if target_audio and target_audio.is_file():
        a_cur = get_media_duration(target_audio) or 0.0
        if not is_speech and eff_master_dur > a_cur > 0:
            from src.services.binaural_spatial_audio import build_seamless_audio_loop
            target_audio = build_seamless_audio_loop(target_audio)

    fade_dur = min(3.0, eff_master_dur)
    fade_start = max(0.0, eff_master_dur - fade_dur)
    afade_filter = f"afade=t=out:st={fade_start:.2f}:d={fade_dur:.2f}"

    v_filter = build_adaptive_resolution_filter(seamless_clips[0], 3840, 2160)
    if n == 1:
        c_dur = get_media_duration(seamless_clips[0]) or 5.0
        v_loops = max(1, int(eff_master_dur / max(1.0, c_dur)) + 2)
        if target_audio and target_audio.is_file():
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-i", str(target_audio),
                "-map", "0:v:0", "-map", "1:a:0",
                "-af", afade_filter,
                "-t", f"{eff_master_dur:.2f}",
                "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-movflags", "+faststart", str(out_master)
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                "-stream_loop", str(v_loops), "-i", str(seamless_clips[0]),
                "-map", "0:v:0", "-t", f"{eff_master_dur:.2f}",
                "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-movflags", "+faststart", str(out_master)
            ]
    else:
        x_dur = min(1.0, eff_master_dur / (n * 3)) if eff_master_dur <= 30.0 else 2.0
        sd_custom = kwargs.get("shot_durations")
        shot_hold_list = [float(d) for d in sd_custom] if (sd_custom and len(sd_custom) == n) else [(eff_master_dur + ((n - 1) * x_dur)) / n] * n
        inputs = []
        for i, c in enumerate(seamless_clips):
            c_dur = get_media_duration(c) or 5.0
            if c_dur >= shot_hold_list[i] - 1.0:
                inputs.extend(["-i", str(c)])
            else:
                v_loops = max(1, int(shot_hold_list[i] / max(1.0, c_dur)) + 2)
                inputs.extend(["-stream_loop", str(v_loops), "-i", str(c)])

        t_fps = int(kwargs.get("target_fps", 24) or 24)
        filter_parts = [f"[{i}:v]{build_adaptive_resolution_filter(c, 3840, 2160, target_fps=t_fps)}[s{i}]" for i, c in enumerate(seamless_clips)]
        prev_tag, curr_offset = "s0", shot_hold_list[0] - x_dur
        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={curr_offset:.2f}[{out_tag}]")
            prev_tag, curr_offset = out_tag, curr_offset + shot_hold_list[i] - x_dur

        if target_audio and target_audio.is_file():
            inputs.extend(["-i", str(target_audio)])
            cmd = [ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[v]", "-map", f"{n}:a", "-af", afade_filter, "-t", f"{eff_master_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]
        else:
            filter_a = [f"[{'0:a' if i == 1 else f'a{i-1}'}][{i}:a]acrossfade=d={x_dur:.2f}[{'a' if i == n - 1 else f'a{i}'}]" for i in range(1, n)]
            cmd = [ffmpeg_bin, "-y", "-nostats", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filter_parts + filter_a), "-map", "[v]", "-map", "[a]", "-t", f"{eff_master_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)]

    t_asm = time.time()
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True, creationflags=_SUBPROCESS_FLAGS)
        dur_asm = time.time() - t_asm
        logger.info(f"ffmpeg_master_rendered: master='{out_master.name}' duration={dur_asm:.2f}s target={eff_master_dur:.2f}s timestamp={time.time()}")
    except subprocess.CalledProcessError as err:
        dur_asm = time.time() - t_asm
        err_msg = (err.stderr or err.stdout or str(err)).strip()
        logger.error(f"failed_to_assemble_4k_master: duration={dur_asm:.2f}s error='{err_msg}' timestamp={time.time()}")
        raise RuntimeError(f"FFmpeg assembly failed: {err_msg}") from err
    return out_master


def assemble_dual_masters(video_clips: list[Path], audio_path: Optional[Path], ep_dir: Path, scene_hold_sec: float = 60.0, crf: int = 22, force_rerun: bool = False, target_duration_sec: Optional[float] = None, **kwargs) -> Dict[str, Path]:
    """Assemble 4K masters in CRF 22 format. Automatically rebuilds if forward cineloops are updated."""
    eff_target_dur = target_duration_sec or kwargs.get("target_duration")
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    m_music, m_narr = ep_dir / "master_4k_ambient.mp4", ep_dir / "master_4k_narration.mp4"
    narr_audio = kwargs.get("narration_audio_path") or (ep_dir / "spoken_narration.mp3")

    c_dur = get_media_duration(m_music) if m_music.is_file() else None
    dur_mis = eff_target_dur and c_dur and abs(c_dur - float(eff_target_dur)) > 2.0
    if force_rerun or not m_music.is_file() or m_music.stat().st_size < 1000 or dur_mis or any(sc.stat().st_mtime > m_music.stat().st_mtime for sc in seamless_clips):
        assemble_4k_master(seamless_clips, audio_path, m_music, scene_hold_sec=scene_hold_sec, crf=crf, target_duration_sec=eff_target_dur)

    if narr_audio and Path(narr_audio).is_file() and Path(narr_audio).stat().st_size > 1000:
        c_dur_n = get_media_duration(m_narr) if m_narr.is_file() else None
        n_mis = eff_target_dur and c_dur_n and abs(c_dur_n - float(eff_target_dur)) > 2.0
        if force_rerun or not m_narr.is_file() or m_narr.stat().st_size < 1000 or n_mis or any(sc.stat().st_mtime > m_narr.stat().st_mtime for sc in seamless_clips):
            if m_music.is_file() and m_music.stat().st_size > 1000:
                t_r, t_dur = time.time(), float(eff_target_dur or get_media_duration(m_music) or 60.0)
                fc = (
                    f"[0:a]volume=0.15[bgm_raw];[1:a]volume=1.0[vox];"
                    f"[bgm_raw][vox]sidechaincompress=threshold=0.015:ratio=14:attack=150:release=800:makeup=1.0[bgm];"
                    f"[bgm][vox]amix=inputs=2:duration=first:dropout_transition=3,apad,afade=t=out:st={max(0, t_dur - 3.0):.2f}:d=3.0[aout]"
                )
                cmd_r = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error", "-i", str(m_music), "-i", str(narr_audio), "-filter_complex", fc, "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-t", f"{t_dur:.2f}", "-movflags", "+faststart", str(m_narr)]
                subprocess.run(cmd_r, check=True, creationflags=_SUBPROCESS_FLAGS)
            else:
                assemble_4k_master(seamless_clips, Path(narr_audio), m_narr, scene_hold_sec=scene_hold_sec, crf=crf, target_duration_sec=eff_target_dur, is_narration=True, **kwargs)
    else:
        m_narr = m_music
    return {"music_master": m_music, "narration_master": m_narr, "nature_master": m_narr}


def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float], force_rerun: bool = False) -> Optional[Path]:
    """Export long-play multi-hour stream loop for primary 4K broadcast master."""
    if not hours or hours <= 0 or not master.is_file():
        return None
    eff_h = float(hours)
    sfx = f"_{int(fade_hours)}h_black" if fade_hours else ""
    lp_path = ep_dir / f"master_4k_{int(eff_h) if eff_h.is_integer() else eff_h}hour{sfx}_broadcast.mp4"
    if force_rerun or not lp_path.is_file() or lp_path.stat().st_size < 1000 or master.stat().st_mtime > lp_path.stat().st_mtime:
        export_long_play_broadcast(source_4k_video=master, output_long_play=lp_path, target_duration_seconds=eff_h * 3600.0, fade_to_black_hours=fade_hours)
    return lp_path


def handle_short_export(master: Path, ep_dir: Path, gen: bool = True) -> Optional[Path]:
    """Generate 9:16 vertical teaser short from 4K master."""
    s_path = ep_dir / "short_9x16_ambient.mp4"
    if master.is_file() and master.stat().st_size > 1000 and (not s_path.is_file() or s_path.stat().st_size < 1000):
        generate_ambient_short(source_4k_video=master, output_short_path=s_path)
    return s_path if s_path.is_file() else (ep_dir / "short_9x16_teaser.mp4" if (ep_dir / "short_9x16_teaser.mp4").is_file() else None)


def export_metadata_packages(sb: AmbientStoryboard, ep_dir: Path, hours: Optional[float], fade_h: Optional[float]) -> Tuple[YouTubeAmbientPackage, ThumbnailABPackage, Dict[str, LocalizedMetadata]]:
    """Generate YouTube packaging, A/B thumbnails, and multi-language SEO."""
    eff_h = hours or 3.0
    pkg_music = generate_youtube_ambient_package(sb.primary_archetype, eff_h, sb.secondary_archetype, fade_h)
    pkg_nature = generate_youtube_ambient_package(sb.primary_archetype, eff_h, sb.secondary_archetype, fade_h)
    pkg_nature.title = f"{pkg_nature.title} | Pure Nature Sounds [4K ASMR]"
    pkg_nature.description = f"100% pure natural ambient soundscape without music.\n\n{pkg_nature.description}"
    for fn, pkg in [("youtube_packaging.json", pkg_music), ("youtube_packaging_nature_only.json", pkg_nature),
                   ("youtube_packaging_30min.json", generate_youtube_ambient_package(sb.primary_archetype, 0.5, sb.secondary_archetype))]:
        (ep_dir / fn).write_text(json.dumps(pkg.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
    st = sb.title.split('~')[0].strip()
    (ep_dir / "youtube_packaging_short.json").write_text(json.dumps({"title": f"Experience {st} in 4K 🌊✨ #shorts", "description": f"Stand directly in front of {st} in 4K.", "tags": [sb.primary_archetype, "shorts", "4k_nature"]}, indent=2, ensure_ascii=False), encoding="utf-8")
    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg_music.title, pkg_music.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2, ensure_ascii=False), encoding="utf-8")
    return pkg_music, ab, loc
