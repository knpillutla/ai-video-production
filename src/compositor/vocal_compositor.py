"""Vocal Song & Lyrical Video Local Compositor.

Handles single-plate 4K visual art, Suno song duration probe,
center-screen native lyrics subtitles, and local single-pass FFmpeg assembly.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

import imageio_ffmpeg

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.mcp.topic_memory.server import remember_topic
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.scripts.local_subtitles import generate_kinetic_ass
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.local_video_qa import run_video_qa_audit


def probe_audio_duration(audio_path: Path | str) -> float:
    """Probe exact duration in seconds of any audio file."""
    path = Path(audio_path)
    if not path.is_file(): return 60.0
    if path.suffix.lower() == ".wav":
        try:
            import wave
            with wave.open(str(path), "rb") as w: return float(w.getnframes()) / float(w.getframerate())
        except Exception: pass
    try:
        proc = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stderr)
        if m: return round(float(m.group(1)) * 3600.0 + float(m.group(2)) * 60.0 + float(m.group(3)), 2)
    except Exception as e: logger.warning(f"probe_audio_duration_failed: {e}")
    return 60.0


async def synthesize_vocal_keyframe(storyboard_data: dict[str, Any], out_path: Path, force_live: bool = False) -> tuple[str, Path]:
    from src.compositor.vocal_image_service import synthesize_vocal_scenes
    paths = await synthesize_vocal_scenes(storyboard_data=storyboard_data, scenes_dir=out_path.parent, num_images=1, force_live=force_live)
    return str(paths[0]), paths[0]


def build_vocal_subtitles(
    storyboard_data: dict[str, Any], language: str, out_ass_path: Path,
    total_duration: float, audio_path: Path | None = None,
) -> tuple[Path, Path]:
    """Generate center-screen (.ass) timed lyrics subtitles in target language script with font management and beat sync."""
    from src.services.font_manager import ensure_language_font
    font_name, fonts_dir = ensure_language_font(language)
    raw_segs = storyboard_data.get("lyrics_segments") or []
    segments = [{"start": float(s["start"]), "end": min(total_duration, float(s["end"])), "text": str(s["text"]).strip()}
                for s in raw_segs if isinstance(s, dict) and s.get("text")]
    min_intro = 4.5
    if audio_path and Path(audio_path).is_file():
        try:
            import numpy as np
            from src.scripts.local_beat_detector import LocalBeatDetector
            cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(audio_path), "-t", "35", "-f", "s16le", "-ac", "1", "-ar", "22050", "-"]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if proc.stdout and len(proc.stdout) > 2000:
                samples = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
                grid = LocalBeatDetector().analyze_audio_buffer(samples=samples, sample_rate=22050, duration_seconds=min(35.0, len(samples) / 22050))
                if grid.drop_timestamps:
                    min_intro = max(4.0, min(30.0, float(grid.drop_timestamps[0])))
                    logger.info(f"vocal_onset_detected: {min_intro:.2f}s using LocalBeatDetector")
        except Exception as e:
            logger.warning(f"beat_detection_failed_fallback: {e}")

    if segments and segments[0]["start"] < min_intro:
        shift = min_intro - segments[0]["start"]
        for s in segments:
            s["start"] = round(min(total_duration - 1.0, s["start"] + shift), 2)
            s["end"] = round(min(total_duration, s["end"] + shift), 2)
    elif not segments:
        lyrics = [l.strip() for l in str(storyboard_data.get("lyrics") or "").splitlines() if l.strip() and not l.startswith("[")]
        lines = lyrics or [storyboard_data.get("title_localized") or storyboard_data.get("title_en") or ""]
        tpl = max(3.5, (total_duration - min_intro) / max(1, len(lines)))
        curr = min_intro
        for l in lines:
            end_t = min(total_duration, curr + tpl)
            segments.append({"start": round(curr, 2), "end": round(end_t, 2), "text": l})
            curr = end_t
    sub_file = generate_kinetic_ass(segments=segments, output_path=out_ass_path, language=language, font_size=52, alignment=5, font_name=font_name)
    try:
        from src.scripts.local_subtitles import generate_srt, generate_vtt
        en_segs = [{"start": float(s["start"]), "end": min(total_duration, float(s["end"])), "text": str(s.get("text_en") or s.get("text")).strip()} for s in raw_segs if isinstance(s, dict)] or segments
        generate_srt(segments=en_segs, output_path=out_ass_path.parent / "captions_en.srt")
        generate_vtt(segments=en_segs, output_path=out_ass_path.parent / "captions_en.vtt")
        generate_srt(segments=segments, output_path=out_ass_path.parent / f"captions_{language}.srt")
        generate_vtt(segments=segments, output_path=out_ass_path.parent / f"captions_{language}.vtt")
    except Exception as e: logger.warning(f"failed_generating_youtube_cc_files: {e}")

    return sub_file, fonts_dir


async def assemble_vocal_video(
    image_paths: list[Path] | Path, song_path: Path, sub_path: Path | None, out_video_path: Path,
    duration: float, fps: int = 30, timeline_cues: list[dict[str, Any]] | None = None,
    fonts_dir: Path | str | None = None, static_canvas: bool = True, enable_vfx: bool = True,
    theme: str | None = None, episode_seed: int = 0,
) -> Path:
    """Fast 2-Stage Assembly: Stage 1 Base Assembly (Static Tripod + xfade + Audio) -> Stage 2 Scene VFX."""
    if out_video_path.is_file() and out_video_path.stat().st_size > 1000:
        logger.info(f"vocal_master_cached: reusing existing render {out_video_path.name}")
        return out_video_path
    out_video_path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    imgs = [image_paths] if isinstance(image_paths, Path) else list(image_paths)

    from src.compositor.vocal_fx import compile_vocal_base_filter_complex, ensure_fx_overlay, resolve_scene_vfx_type
    base_target = out_video_path.parent / f"_temp_base_{out_video_path.name}" if enable_vfx else out_video_path

    # Stage 1: Fast Base Assembly on Static Tripod (Images + xfade + Audio + Subtitles)
    base_filter = compile_vocal_base_filter_complex(len(imgs), duration, sub_path=sub_path, fonts_dir=fonts_dir, fps=fps)
    img_args = [arg for p in imgs for arg in ("-loop", "1", "-t", f"{duration:.2f}", "-i", str(p))]
    cmd_base = [
        ffmpeg, "-y", *img_args, "-i", str(song_path), "-t", f"{duration:.2f}",
        "-filter_complex", base_filter, "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", "-r", str(fps),
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-threads", "8", "-shortest", str(base_target),
    ]
    proc = await asyncio.create_subprocess_exec(*cmd_base, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_msg = stderr.decode(errors="replace")
        logger.error(f"ffmpeg_base_render_failed: {err_msg[-1200:]}")
        raise RuntimeError(f"FFmpeg base render error:\n{err_msg[-1200:]}")

    if not enable_vfx:
        return out_video_path

    # Stage 2: Fast Single-Overlay VFX Pass across Timeline (Scene-Matched & Seed-Randomized)
    fx_type = resolve_scene_vfx_type(theme=theme, timeline_cues=timeline_cues)
    vfx_clip = ensure_fx_overlay(fx_type, seed=episode_seed)
    logger.info(f"vocal_vfx_applied: fx_type={fx_type}, seed={episode_seed % 30}, clip={vfx_clip.name}")
    vfx_filter = "[1:v]colorkey=0x000000:0.04:0.12,format=yuva420p,scale=3840:2160:flags=fast_bilinear[ov];[0:v][ov]overlay=x=0:y=0:format=auto[v_out]"
    cmd_vfx = [
        ffmpeg, "-y", "-i", str(base_target), "-stream_loop", "-1", "-i", str(vfx_clip),
        "-filter_complex", vfx_filter, "-map", "[v_out]", "-map", "0:a",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "copy",
        "-t", f"{duration:.2f}", "-threads", "8", str(out_video_path),
    ]
    proc_vfx = await asyncio.create_subprocess_exec(*cmd_vfx, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, stderr_vfx = await proc_vfx.communicate()
    base_target.unlink(missing_ok=True)
    if proc_vfx.returncode != 0:
        err_msg = stderr_vfx.decode(errors="replace")
        logger.error(f"ffmpeg_vfx_render_failed: {err_msg[-1200:]}")
        raise RuntimeError(f"FFmpeg VFX overlay error:\n{err_msg[-1200:]}")
    return out_video_path


async def execute_vocal_pipeline(
    pipeline: Any, user_id: Any, episode: Any, ep_dir: Path, scenes_dir: Path, stems_dir: Path,
    renders_dir: Path, strategy: Any, language: str = "en", gender: str = "duet",
    force_live: bool = False, dry_run: bool = False, show_slug: str = "default_universe",
    music_style: str | None = None, similar_to: str | None = None, country: str | None = None,
    culture: str | None = None, idea: str | None = None, script: str | None = None,
    theme: str | None = None, art_style: str | None = None, profile: str = "development",
    **kwargs: Any,
) -> Path | None:
    """Execute end-to-end vocal song lyrical production with song length lock and local assembly."""
    t_start = time.perf_counter()
    sb_path = ep_dir / "storyboard.json"
    sb_data = json.loads(sb_path.read_text(encoding="utf-8")) if sb_path.is_file() and sb_path.stat().st_size > 50 else None
    num_imgs = int(kwargs.get("num_images") or 1)

    if not sb_data:
        eff_idea, eff_theme = idea or theme, theme or idea or ""
        gem_in = {"title": episode.title, "duration_seconds": int(episode.duration_seconds), "language": language, "genre": "vocal", "idea": eff_idea, "art_style": art_style, "music_style": music_style, "similar_to": similar_to, "country": country, "culture": culture, "gender": gender, "theme": eff_theme, "num_images": num_imgs}
        await storage_service.save_json(ep_dir / "gemini_inputs.json", gem_in)
        p = strategy.build_gemini_prompt(**gem_in)
        (ep_dir / "gemini_prompt.txt").write_text(p, encoding="utf-8")
        sb_data = await pipeline.llm.generate_structured(p, schema=strategy.build_gemini_schema())
        await storage_service.save_json(sb_path, sb_data)

    lyrics = sb_data.get("lyrics") or ""
    await remember_topic(
        topic=episode.title, metadata={"language": language, "style": music_style, "similar_to": similar_to, "genre": "vocal"},
        final_story=lyrics, episode_id=str(episode.id), show_slug=show_slug, user_id=str(user_id),
    )

    # 1. Suno Track & Duration Lock (Rule 3 Tier 1 Disk Check)
    bgm_path = stems_dir / "bgm_master.wav"
    if not (bgm_path.is_file() and bgm_path.stat().st_size > 1000):
        suno_tags = sb_data.get("suno_tags") or "romantic melody, acoustic, duet"
        vocal_gen = sb_data.get("vocal_gender") or gender or "duet"
        await pipeline.music.generate_to_file(
            output_path=bgm_path, genre=suno_tags, duration_seconds=float(episode.duration_seconds),
            lyrics=lyrics, vocal_gender=vocal_gen, title=episode.title, force_live=force_live,
        )
        rights_ledger.record_asset(episode.id, AssetType.MUSIC, str(bgm_path), "Suno/CineAI", "v3.5-pro", CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"SUNO-{episode.id}", True)
    else:
        logger.info(f"vocal_suno_cached: reusing existing track {bgm_path.name} ({bgm_path.stat().st_size} bytes)")

    clean_audio, noise_stem = stems_dir / "bgm_cleaned.mp3", stems_dir / "noise_stem.wav"
    if not (clean_audio.is_file() and clean_audio.stat().st_size > 1000):
        try:
            from src.services.audio_denoise_service import separate_and_denoise_soundtrack
            separate_and_denoise_soundtrack(input_audio=bgm_path, clean_output=clean_audio, noise_stem_output=noise_stem, force_rerun=force_live)
        except Exception as e:
            logger.warning(f"vocal_denoise_fallback: {e}")
            clean_audio = bgm_path
    active_audio = clean_audio if (clean_audio.is_file() and clean_audio.stat().st_size > 1000) else bgm_path

    actual_dur = probe_audio_duration(active_audio)
    episode.duration_seconds = int(round(actual_dur))
    repo.save_episode(episode)

    # 2. Keyframes & Subtitles with LoRA Consistency (Rule 3 Tier 1 Disk Check)
    from src.compositor.vocal_image_service import synthesize_vocal_scenes
    eff_net = kwargs.get("network") or show_slug
    img_paths = await synthesize_vocal_scenes(
        storyboard_data=sb_data, scenes_dir=scenes_dir, num_images=num_imgs,
        user_id=str(user_id), network=eff_net, force_live=force_live, episode_id=episode.id,
        use_loras=kwargs.get("use_loras", False),
    )
    primary_img = img_paths[0] if img_paths else scenes_dir / "scene_01.jpg"

    sub_path = ep_dir / "subtitles" / f"kinetic_{language}.ass"
    sub_path, fonts_dir = build_vocal_subtitles(sb_data, language, sub_path, actual_dur, audio_path=active_audio)

    # 3. Two-Stage Preview & Master Assembly (Rule 22 Quality Gate)
    anim_cues = sb_data.get("animation_timeline")
    render_name = f"master_16x9_ep{episode.episode_number:02d}_{language}.mp4" if language and language != "en" else f"master_16x9_ep{episode.episode_number:02d}.mp4"
    final_video = renders_dir / render_name

    preview_dur = min(30.0, actual_dur)
    prev_name = f"preview_30s_ep{episode.episode_number:02d}_{language}.mp4" if language and language != "en" else f"preview_30s_ep{episode.episode_number:02d}.mp4"
    preview_video, ffmpeg_bin = renders_dir / prev_name, imageio_ffmpeg.get_ffmpeg_exe()

    norm_audio = stems_dir / "bgm_normalized_48k.mp3"
    if norm_audio.is_file() and norm_audio.stat().st_size > 1000: active_audio = norm_audio
    else:
        try:
            subprocess.run([ffmpeg_bin, "-y", "-i", str(active_audio), "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=7.0", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000", str(norm_audio)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            active_audio = norm_audio
        except Exception: pass

    if final_video.is_file() and final_video.stat().st_size > 1000:
        if not (preview_video.is_file() and preview_video.stat().st_size > 1000):
            try: subprocess.run([ffmpeg_bin, "-y", "-i", str(final_video), "-t", f"{preview_dur:.2f}", "-c", "copy", str(preview_video)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            except Exception: pass
        logger.info(f"vocal_master_cached: reusing existing master render {final_video.name}")
        return final_video

    full_conf = kwargs.get("full_confirmed", False)
    ep_seed = abs(hash(str(episode.id))) % 30
    eff_theme_vfx = theme or (sb_data.get("hook_thesis") if sb_data else None) or episode.title

    if not full_conf and actual_dur > 30.0 and not dry_run:
        if not (preview_video.is_file() and preview_video.stat().st_size > 1000):
            print(f"\n[~] Stage 1/2: Generating 30s fast preview video for review...")
            await assemble_vocal_video(image_paths=img_paths, song_path=active_audio, sub_path=None, out_video_path=preview_video, duration=preview_dur, timeline_cues=anim_cues, fonts_dir=fonts_dir, theme=eff_theme_vfx, episode_seed=ep_seed)
        print(f"\n[+] 30s Fast Preview Video Ready: {preview_video.name}")
        if kwargs.get("preview_only", False): return preview_video
        cg = kwargs.get("custom_gate_input_fn")
        proceed = cg(f"Proceed to render full master? (y/N): ") if cg else (input(f"\n[?] 30s preview ready ({preview_video.name}). Render full {actual_dur:.0f}s video? [y/N]: ").strip().lower() in ("y", "yes") if hasattr(sys.stdin, "isatty") and sys.stdin.isatty() else False)
        if not proceed:
            print(f"[i] Pausing at 30s preview. Pass --full-confirmed to render full {actual_dur:.0f}s master.")
            return preview_video

    if dry_run:
        final_video.touch()
    else:
        print(f"\n[~] Rendering full {actual_dur:.0f}s master video...")
        await assemble_vocal_video(image_paths=img_paths, song_path=active_audio, sub_path=None, out_video_path=final_video, duration=actual_dur, timeline_cues=anim_cues, fonts_dir=fonts_dir, theme=eff_theme_vfx, episode_seed=ep_seed)
        if not (preview_video.is_file() and preview_video.stat().st_size > 1000):
            try: subprocess.run([ffmpeg_bin, "-y", "-i", str(final_video), "-t", f"{preview_dur:.2f}", "-c", "copy", str(preview_video)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            except Exception: pass

    thumb_path = ep_dir / "thumbnails" / f"thumb_ep{episode.episode_number:02d}_{language}.jpg"
    headline = sb_data.get("title_localized") or sb_data.get("title_en") or episode.title
    thumb_img = img_paths[-1] if img_paths else primary_img
    generate_episodic_thumbnail(output_path=thumb_path, base_image_path=thumb_img, badge_config=EpisodicBadgeConfig(episode_number=episode.episode_number, language=language, style="pill", position="top_left", custom_label=language.upper()), headline=headline, enable_vfx=True)
    qa = run_video_qa_audit(final_video, actual_dur)
    episode.status, episode.master_video_path, episode.duration_seconds = ("completed" if qa.passed else "review_required"), str(final_video), int(round(actual_dur))
    from src.compositor.vocal_packaging import export_vocal_production_bundle
    export_vocal_production_bundle(episode=episode, ep_dir=ep_dir, sb_data=sb_data, actual_dur=actual_dur, t_start=t_start, language=language, keyframe_path=primary_img, master_video_path=final_video)
    repo.save_episode(episode)
    logger.info(f"vocal_pipeline_complete: video={final_video.name}, dur={actual_dur:.1f}s, qa={qa.scores.composite_score}, cost=${episode.actual_spend_usd:.4f}, elapsed={round(time.perf_counter() - t_start, 1)}s")
    return final_video

__all__ = ["probe_audio_duration", "synthesize_vocal_keyframe", "build_vocal_subtitles", "assemble_vocal_video", "execute_vocal_pipeline"]
