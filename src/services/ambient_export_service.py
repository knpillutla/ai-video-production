from __future__ import annotations
import json, subprocess, time
from pathlib import Path
from typing import Dict, Optional, Tuple, TYPE_CHECKING
import imageio_ffmpeg

from src.core.telemetry import logger
from src.services.ambient_metadata_packager import YouTubeAmbientPackage, generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import LocalizedMetadata, localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import ThumbnailABPackage, generate_thumbnail_ab_variants

if TYPE_CHECKING:
    from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


def get_media_duration(media_path: Path) -> float:
    """Probe the exact duration of a media file in seconds."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(media_path)], capture_output=True, text=True, errors="ignore")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", res.stderr)
        if m:
            return float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 5.0


def probe_clip_geometry(clip_path: Path) -> Tuple[int, int]:
    """Probe the exact width and height of an input clip."""
    try:
        import re
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
        m = re.search(r",\s*(\d{3,4})x(\d{3,4})", res.stderr)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return 1920, 1080


def build_adaptive_resolution_filter(clip_path: Path, target_w: int = 3840, target_h: int = 2160) -> str:
    """Build a resolution-aware video filter: no-op for native 4K, direct Lanczos for 16:9, safe pad for non-standard."""
    w, h = probe_clip_geometry(clip_path)
    if w == target_w and h == target_h:
        return "setsar=1"
    target_aspect = target_w / target_h
    clip_aspect = (w / h) if h > 0 else target_aspect
    if abs(clip_aspect - target_aspect) < 0.01:
        return f"scale={target_w}:{target_h}:flags=lanczos,setsar=1"
    return f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1"


def build_seamless_forward_cineloop(clip_path: Path, xfade_dur: float = 1.2, crf: int = 22) -> Path:
    """Transform short 5s/10s AI diffusion motion clip into an infinitely loopable forward-flowing cineloop (zero reverse flow, zero flicker)."""
    if clip_path.name.endswith("_fwd_seamless.mp4") and clip_path.is_file():
        return clip_path

    base_stem = clip_path.stem.replace("_fwd_seamless", "")
    sp_file = clip_path.parent / "screenplay.json"
    if "p" in base_stem and sp_file.is_file():
        try:
            import json
            sp = json.loads(sp_file.read_text(encoding="utf-8"))
            idx = int("".join(filter(str.isdigit, base_stem)) or "1")
            scs = sp.get("scenes", [])
            if idx - 1 < len(scs) and scs[idx - 1].get("motion_type") in ("ken_burns", "static", "local_zoompan"):
                return clip_path
        except Exception:
            pass

    out_seamless = clip_path.parent / f"{base_stem}_fwd_seamless.mp4"
    duration = get_media_duration(clip_path)
    if duration <= xfade_dur + 0.5:
        return clip_path

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    check = subprocess.run([ffmpeg_bin, "-i", str(clip_path)], capture_output=True, text=True, errors="ignore")
    has_audio = "Audio:" in check.stderr

    if out_seamless.is_file() and out_seamless.stat().st_size > 1000:
        if has_audio:
            check_out = subprocess.run([ffmpeg_bin, "-i", str(out_seamless)], capture_output=True, text=True, errors="ignore")
            if "Audio:" in check_out.stderr:
                return out_seamless
        else:
            return out_seamless

    split_offset = max(0.1, duration - xfade_dur)
    if has_audio:
        filter_graph = (
            f"[0:v]split=2[h][t];"
            f"[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];"
            f"[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];"
            f"[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v];"
            f"[0:a]atrim=0:{split_offset:.2f},asetpts=PTS-STARTPTS[a]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", str(crf),
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            str(out_seamless),
        ]
    else:
        filter_graph = (
            f"[0:v]split=2[h][t];"
            f"[t]trim=start={split_offset:.2f}:end={duration:.2f},setpts=PTS-STARTPTS,fps=24[t1];"
            f"[h]trim=start=0:end={split_offset:.2f},setpts=PTS-STARTPTS,fps=24[h1];"
            f"[t1][h1]xfade=transition=fade:duration={xfade_dur:.2f}:offset=0,fps=24,format=yuv420p[v]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-i", str(clip_path),
            "-filter_complex", filter_graph,
            "-map", "[v]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", str(crf),
            str(out_seamless),
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return out_seamless
    except Exception as err:
        logger.warning(f"forward_cineloop_fallback: {err}")
        return clip_path


def assemble_4k_master(video_clips: list[Path], audio_path: Optional[Path], out_master: Path, scene_hold_sec: float = 60.0, crf: int = 22, target_duration_sec: Optional[float] = None, is_narration: bool = False, **kwargs) -> Path:
    """Assemble relaxing 4K master with seamless forward cineloops and crossfades in CRF 22 format."""
    from src.services.procedural_foley import synthesize_foley_stem
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    n, x_dur = len(seamless_clips), 2.0
    target_audio = audio_path
    if not target_audio or not target_audio.is_file():
        has_clip_audio = all("Audio:" in subprocess.run([ffmpeg_bin, "-i", str(c)], capture_output=True, text=True, errors="ignore").stderr for c in seamless_clips)
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

        filter_parts = [f"[{i}:v]{build_adaptive_resolution_filter(c, 3840, 2160)}[s{i}]" for i, c in enumerate(seamless_clips)]
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
        subprocess.run(cmd, capture_output=True, text=True, check=True)
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
                t_r = time.time()
                t_dur = float(eff_target_dur or get_media_duration(m_music) or 60.0)
                cmd_r = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error", "-i", str(m_music), "-i", str(narr_audio), "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-af", f"apad,afade=t=out:st={max(0, t_dur - 3.0):.2f}:d=3.0", "-t", f"{t_dur:.2f}", "-movflags", "+faststart", str(m_narr)]
                subprocess.run(cmd_r, check=True)
                logger.info(f"fast_narration_master_remuxed: duration={time.time() - t_r:.2f}s target={t_dur:.2f}s")
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
    pkg_nature.title, pkg_nature.description = f"{pkg_nature.title} | Pure Nature Sounds [4K ASMR]", f"100% pure natural ambient soundscape without music.\n\n{pkg_nature.description}"
    for fn, pkg in [("youtube_packaging.json", pkg_music), ("youtube_packaging_nature_only.json", pkg_nature),
                   ("youtube_packaging_30min.json", generate_youtube_ambient_package(sb.primary_archetype, 0.5, sb.secondary_archetype))]:
        (ep_dir / fn).write_text(json.dumps(pkg.model_dump(), indent=2), encoding="utf-8")
    st = sb.title.split('~')[0].strip()
    (ep_dir / "youtube_packaging_short.json").write_text(json.dumps({"title": f"Experience {st} in 4K 🌊✨ #shorts", "description": f"Stand directly in front of {st} in 4K.", "tags": [sb.primary_archetype, "shorts", "4k_nature"]}, indent=2), encoding="utf-8")
    ab = generate_thumbnail_ab_variants(sb.primary_archetype)
    (ep_dir / "thumbnail_ab_variants.json").write_text(json.dumps(ab.model_dump(), indent=2), encoding="utf-8")
    loc = localize_metadata_for_languages(sb.primary_archetype, pkg_music.title, pkg_music.description)
    (ep_dir / "localized_metadata.json").write_text(json.dumps({k: v.model_dump() for k, v in loc.items()}, indent=2), encoding="utf-8")
    return pkg_music, ab, loc
