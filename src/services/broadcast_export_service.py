"""Broadcast Packaging and Export Utilities (long-play stretching, shorts, localized metadata)."""

from __future__ import annotations
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, Optional, TYPE_CHECKING
import imageio_ffmpeg

from src.core.step_logger import log_pipeline_step
from src.core.telemetry import logger
from src.services.ambient_export_service import build_adaptive_resolution_filter, get_media_duration
from src.services.ambient_metadata_packager import generate_youtube_ambient_package
from src.services.ambient_shorts_extractor import generate_ambient_short
from src.services.ambient_translator import localize_metadata_for_languages
from src.services.long_play_stretcher import export_long_play_broadcast
from src.services.thumbnail_ab_packager import generate_thumbnail_ab_variants
from src.services.topic_memory import topic_memory

if TYPE_CHECKING:
    from src.studios.screenplay_models import AmbientStoryboard


from src.services.cineloop_service import build_seamless_forward_cineloop


def assemble_4k_master(
    seamless_clips: list[Path],
    audio_path: Optional[Path],
    out_master: Path,
    scene_hold_sec: float = 60.0,
    x_dur: float = 1.0,
    crf: int = 22,
    target_duration_sec: Optional[float] = None,
    shot_durations: Optional[list[float]] = None,
) -> Path:
    """Concatenate 4K cineloops into a master broadcast matching target_duration_sec or music track."""
    out_master.parent.mkdir(parents=True, exist_ok=True)
    n = len(seamless_clips)
    if n == 0:
        raise ValueError("Cannot assemble 4K master: zero valid seamless clips provided.")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    v_filter = build_adaptive_resolution_filter(seamless_clips[0], 3840, 2160)

    a_dur = get_media_duration(audio_path) if (audio_path and audio_path.is_file()) else 0.0
    target_dur = float(target_duration_sec) if (target_duration_sec and target_duration_sec > 0) else (a_dur if a_dur > 5.0 else scene_hold_sec)

    fade_dur = min(3.0, target_dur)
    fade_start = max(0.0, target_dur - fade_dur)
    afade_filter = f"afade=t=out:st={fade_start:.2f}:d={fade_dur:.2f}"

    if n == 1:
        c_dur = get_media_duration(seamless_clips[0]) or 5.0
        v_loops = max(1, int(target_dur / max(1.0, c_dur)) + 2)
        in_args = ["-stream_loop", str(v_loops), "-i", str(seamless_clips[0])]
        if audio_path and audio_path.is_file():
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                *in_args, "-i", str(audio_path), "-map", "0:v:0", "-map", "1:a:0",
                "-af", afade_filter, "-t", f"{target_dur:.2f}", "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                *in_args, "-map", "0:v:0", "-t", f"{target_dur:.2f}", "-vf", v_filter,
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-movflags", "+faststart", str(out_master)
            ]
    else:
        hold_list = [float(d) for d in shot_durations] if (shot_durations and len(shot_durations) == n) else [max(6.0, (target_dur + ((n - 1) * x_dur)) / n)] * n
        inputs = []
        for i, c in enumerate(seamless_clips):
            c_dur = get_media_duration(c) or 5.0
            c_hold = hold_list[i] if i < len(hold_list) else c_dur
            if c_dur < c_hold - 0.5:
                v_loops = max(1, int(c_hold / max(1.0, c_dur)) + 2)
                inputs.extend(["-stream_loop", str(v_loops)])
            inputs.extend(["-i", str(c)])

        filter_parts = [f"[{i}:v]{build_adaptive_resolution_filter(c, 3840, 2160)}[s{i}]" for i, c in enumerate(seamless_clips)]
        prev_tag, curr_offset = "s0", max(0.1, hold_list[0] - x_dur)
        for i in range(1, n):
            out_tag = f"v{i}" if i < n - 1 else "v"
            filter_parts.append(f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={max(0.1, curr_offset):.2f}[{out_tag}]")
            prev_tag = out_tag
            curr_offset += max(0.1, (hold_list[i] - x_dur) if i < n - 1 else hold_list[i])
        target_dur = round(curr_offset, 2)

        if audio_path and audio_path.is_file():
            inputs.extend(["-i", str(audio_path)])
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                *inputs, "-filter_complex", ";".join(filter_parts),
                "-map", "[v]", "-map", f"{n}:a", "-af", afade_filter, "-t", f"{target_dur:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(out_master)
            ]
        else:
            cmd = [
                ffmpeg_bin, "-y", "-nostats", "-loglevel", "error",
                *inputs, "-filter_complex", ";".join(filter_parts),
                "-map", "[v]", "-t", f"{target_dur:.2f}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-threads", "4", "-crf", str(crf),
                "-movflags", "+faststart", str(out_master)
            ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as err:
        err_msg = (err.stderr or err.stdout or str(err)).strip()
        logger.error(f"failed_to_assemble_4k_master: {err_msg}")
        raise RuntimeError(f"FFmpeg assembly failed: {err_msg}") from err
    return out_master


def assemble_dual_masters(
    video_clips: list[Path],
    audio_path: Optional[Path] = None,
    ep_dir: Optional[Path] = None,
    audio_track: Optional[Path] = None,
    target_fps: int = 24,
    force_rerun: bool = False,
    crf: int = 22,
    target_duration_sec: Optional[float] = None,
    **kwargs,
) -> Dict[str, Path]:
    """Assemble 4K masters matching user requested duration or complete music track length."""
    eff_audio = audio_path or audio_track
    if not ep_dir and video_clips:
        ep_dir = video_clips[0].parent

    eff_target_dur = target_duration_sec or kwargs.get("target_duration")
    sd_custom = kwargs.get("shot_durations")
    seamless_clips = [build_seamless_forward_cineloop(c, crf=crf) for c in video_clips]
    master_narr = ep_dir / "master_4k_narration.mp4"
    master_music = ep_dir / "master_4k_ambient.mp4"
    narr_audio = kwargs.get("narration_audio_path") or (ep_dir / "spoken_narration.mp3")
    has_narration = bool(narr_audio and Path(narr_audio).is_file() and Path(narr_audio).stat().st_size > 1000)

    if has_narration:
        n_dur = get_media_duration(narr_audio) if (narr_audio and Path(narr_audio).is_file()) else None
        t_dur = float(n_dur or eff_target_dur or sum(get_media_duration(c) or 10.0 for c in seamless_clips) or 60.0)
        mixed_audio = ep_dir / "master_audio_narrated_ducked.mp3"
        if force_rerun or not mixed_audio.is_file() or mixed_audio.stat().st_size < 1000:
            cmd_mix = [
                imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error",
                "-i", str(eff_audio), "-i", str(narr_audio),
                "-filter_complex", f"[0:a]aloop=loop=-1:size=2e+09,volume=0.22,atrim=0:{t_dur:.2f}[bgm];[1:a]volume=1.0,apad,atrim=0:{t_dur:.2f}[vox];[bgm][vox]amix=inputs=2:duration=longest:dropout_transition=0,afade=t=out:st={max(0.0, t_dur - 3.0):.2f}:d=3.0[aout]",
                "-map", "[aout]", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
                "-t", f"{t_dur:.2f}", str(mixed_audio),
            ]
            subprocess.run(cmd_mix, check=True)

        c_dur_n = get_media_duration(master_narr) if master_narr.is_file() else None
        n_mis = t_dur and c_dur_n and abs(c_dur_n - float(t_dur)) > 2.0
        needs_n = force_rerun or not master_narr.is_file() or master_narr.stat().st_size < 1000 or n_mis or any(sc.stat().st_mtime > master_narr.stat().st_mtime for sc in seamless_clips)
        log_pipeline_step("checking master", "4K Narration Master", "started", metadata={"file": master_narr.name, "target_duration": t_dur})
        if needs_n:
            assemble_4k_master(seamless_clips, mixed_audio, master_narr, crf=crf, target_duration_sec=t_dur, shot_durations=sd_custom)
            log_pipeline_step("checking master", "4K Narration Master", "completed", "assembled master_4k_narration.mp4 as primary master", {"file": master_narr.name, "crf": crf, "cost": "$0.00"})
        else:
            log_pipeline_step("checking master", "4K Narration Master", "completed", "master_4k_narration.mp4 exists, render not recreated", {"file": master_narr.name, "cost": "$0.00"})

        log_pipeline_step("checking master", "4K Ambient Master", "started", metadata={"file": master_music.name})
        needs_m = force_rerun or not master_music.is_file() or master_music.stat().st_size < 1000 or master_narr.stat().st_mtime > master_music.stat().st_mtime
        if needs_m:
            cmd_m = [
                imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error",
                "-i", str(master_narr), "-i", str(eff_audio),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
                "-t", f"{t_dur:.2f}", "-movflags", "+faststart", str(master_music),
            ]
            subprocess.run(cmd_m, check=True)
            log_pipeline_step("checking master", "4K Ambient Master", "completed", "remuxed master_4k_ambient.mp4 (music-only edition)", {"file": master_music.name, "cost": "$0.00"})
        else:
            log_pipeline_step("checking master", "4K Ambient Master", "completed", "master_4k_ambient.mp4 exists, render not recreated", {"file": master_music.name, "cost": "$0.00"})

    else:
        cached_dur = get_media_duration(master_music) if master_music.is_file() else None
        d_mis = eff_target_dur is not None and cached_dur is not None and abs(cached_dur - float(eff_target_dur)) > 2.0
        needs_rebuild = force_rerun or not master_music.is_file() or master_music.stat().st_size < 1000 or d_mis or any(sc.stat().st_mtime > master_music.stat().st_mtime for sc in seamless_clips)
        log_pipeline_step("checking master", "4K Ambient Master", "started", metadata={"file": master_music.name, "target_duration": eff_target_dur})
        if needs_rebuild:
            assemble_4k_master(seamless_clips, eff_audio, master_music, crf=crf, target_duration_sec=eff_target_dur)
            log_pipeline_step("checking master", "4K Ambient Master", "completed", "assembled master_4k_ambient.mp4", {"file": master_music.name, "crf": crf, "cost": "$0.00"})
        else:
            log_pipeline_step("checking master", "4K Ambient Master", "completed", "master_4k_ambient.mp4 exists, render not recreated", {"file": master_music.name, "cost": "$0.00"})
        master_narr = master_music
        master_nature = ep_dir / "master_4k_nature.mp4"
        foley_audio = kwargs.get("foley_audio_path") or (ep_dir / "foley_ambient.mp3")
        f_dur = get_media_duration(master_music) or eff_target_dur or 60.0
        if not (foley_audio and Path(foley_audio).is_file() and Path(foley_audio).stat().st_size > 1000):
            foley_audio = ep_dir / "foley_ambient.mp3"
            if not foley_audio.is_file():
                try:
                    subprocess.run([
                        imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error",
                        "-f", "lavfi", "-i", "anoisesrc=color=brown:amplitude=0.06:sample_rate=48000,lowpass=f=450,highpass=f=35,volume=0.9",
                        "-t", f"{f_dur:.2f}", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000", str(foley_audio),
                    ], check=True)
                except Exception:
                    foley_audio = None

        needs_nature = force_rerun or not master_nature.is_file() or master_nature.stat().st_size < 1000 or (master_music.is_file() and master_music.stat().st_mtime > master_nature.stat().st_mtime)
        log_pipeline_step("checking master", "4K Pure Nature Master", "started", metadata={"file": master_nature.name})
        if needs_nature and master_music.is_file():
            cmd_nat = [
                imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-nostats", "-loglevel", "error", "-i", str(master_music),
                *(["-i", str(foley_audio), "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"] if foley_audio and Path(foley_audio).is_file() else ["-map", "0:v:0", "-an"]),
                "-c:v", "copy", "-t", f"{f_dur:.2f}", "-movflags", "+faststart", str(master_nature),
            ]
            try:
                subprocess.run(cmd_nat, check=True)
                log_pipeline_step("checking master", "4K Pure Nature Master", "completed", "remuxed master_4k_nature.mp4", {"file": master_nature.name, "cost": "$0.00"})
            except Exception as n_err:
                logger.warning(f"remux_nature_master_failed: {n_err}")
                master_nature = master_music
        else:
            log_pipeline_step("checking master", "4K Pure Nature Master", "completed", "master_4k_nature.mp4 exists", {"file": master_nature.name, "cost": "$0.00"})

    primary = master_narr if has_narration else master_music
    nat_primary = master_music if has_narration else master_nature
    return {
        "master_4k": primary, "master_video_path": primary, "music_master": master_music,
        "narrative_master": master_narr, "narration_master": master_narr,
        "nature_master": nat_primary, "master_nature": nat_primary, "master_1080p": primary,
    }

def handle_long_play_export(master: Path, ep_dir: Path, hours: Optional[float], fade_hours: Optional[float], nature_master: Optional[Path] = None) -> Optional[Path]:
    """Export long-play multi-hour stream loop for primary 4K broadcast master and pure nature edition."""
    eff_hours = hours if (hours and hours > 0) else 3.0
    suffix = f"_{int(fade_hours)}h_black" if fade_hours else ""
    hour_label = int(eff_hours) if eff_hours.is_integer() else eff_hours
    lp_path = ep_dir / f"master_4k_{hour_label}hour{suffix}_broadcast.mp4"
    if master.is_file() and (not lp_path.is_file() or lp_path.stat().st_size < 1000):
        export_long_play_broadcast(master, lp_path, eff_hours * 3600.0, fade_to_black_hours=fade_hours)

    if nature_master and nature_master.is_file() and nature_master.resolve() != master.resolve():
        nat_sfx = "_music_only" if "ambient" in nature_master.name or "music" in nature_master.name else "_nature_only"
        lp_nat_path = ep_dir / f"master_4k_{hour_label}hour{nat_sfx}{suffix}_broadcast.mp4"
        if not lp_nat_path.is_file() or lp_nat_path.stat().st_size < 1000:
            export_long_play_broadcast(nature_master, lp_nat_path, eff_hours * 3600.0, fade_to_black_hours=fade_hours)

    return lp_path if lp_path.is_file() else None

def export_metadata_packages(sb: Any, ep_dir: Path) -> Dict[str, Any]:
    """Generate YouTube SEO, Multi-Language, and A/B Thumbnail metadata."""
    arch = str(getattr(sb, "primary_archetype", None) or getattr(sb, "cluster", None) or "cities")
    title = str(getattr(sb, "title", "Studio 4K Showcase"))
    desc = str(getattr(sb, "story_topic", title) or title)
    yt_pkg, loc_pkg, ab_pkg = generate_youtube_ambient_package(arch), localize_metadata_for_languages(arch, title, desc), generate_thumbnail_ab_variants(arch)
    loc_dict = {k: (v.model_dump() if hasattr(v, "model_dump") else v) for k, v in loc_pkg.items()}
    for name, data in [("youtube_packaging.json", yt_pkg.model_dump()), ("youtube_packaging_nature_only.json", yt_pkg.model_dump()), ("localized_metadata.json", loc_dict), ("thumbnail_ab_testing.json", ab_pkg.model_dump())]:
        (ep_dir / name).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return {"youtube": yt_pkg.model_dump(), "youtube_nature_only": yt_pkg.model_dump(), "localized": loc_dict, "thumbnail_ab": ab_pkg.model_dump()}

async def handle_short_export(
    sb: AmbientStoryboard, ep_dir: Path, video_clips: list[Path], audio_track: Path,
    t_start: float, hours: Optional[float], fade_h: Optional[float], force_rerun: bool,
    narration_audio_path: Optional[Path] = None, target_duration_sec: Optional[float] = None,
    shot_durations: Optional[List[float]] = None, **kwargs: Any,
) -> Dict[str, Any]:
    """Export 9:16 vertical short and return completed artifact package."""
    dual_res = assemble_dual_masters(
        video_clips=video_clips, audio_path=audio_track, ep_dir=ep_dir,
        force_rerun=force_rerun, narration_audio_path=narration_audio_path,
        target_duration_sec=target_duration_sec, shot_durations=shot_durations,
    )

    short_path = ep_dir / "short_9x16_teaser.mp4"
    if force_rerun or not short_path.is_file() or short_path.stat().st_size < 1000:
        log_pipeline_step("checking master", "9:16 Vertical Short Teaser", "started", metadata={"file": "short_9x16_teaser.mp4"})
        try:
            short_path = generate_ambient_short(dual_res["master_4k"], short_path)
            log_pipeline_step("checking master", "9:16 Vertical Short Teaser", "completed", "assembled short_9x16_teaser.mp4", {"file": "short_9x16_teaser.mp4", "cost": "$0.00"})
        except Exception as s_ex:
            logger.warning(f"short_generation_failed: {s_ex}")
            log_pipeline_step("checking master", "9:16 Vertical Short Teaser", "failed", str(s_ex))
    else:
        log_pipeline_step("checking master", "9:16 Vertical Short Teaser", "completed", "short teaser exists, short teaser not recreated", {"file": "short_9x16_teaser.mp4", "cost": "$0.00"})

    meta = export_metadata_packages(sb, ep_dir)
    try: await topic_memory.record_production(topic=sb.title, genre=f"nature_{sb.cluster}", tags=meta.get("youtube", {}).get("seo_tags", []), episode_id=ep_dir.name)
    except Exception as tm_ex: logger.warning(f"topic_memory_record_warning: {tm_ex}")
    return {
        "status": "success", "production_type": "short_and_dual_master",
        "episode_id": ep_dir.name, "title": getattr(sb, "title", ep_dir.name),
        "master_video_path": str(dual_res["master_4k"]), "master_4k_path": str(dual_res["master_4k"]),
        "master_nature_video_path": str(dual_res.get("nature_master", dual_res["master_4k"])),
        "short_video_path": str(short_path), "master_narration_path": str(dual_res.get("narration_master", dual_res["master_4k"])),
        "render_time_seconds": round(time.time() - t_start, 2), "video_clips": [str(c) for c in video_clips], "metadata": meta,
    }
