"""Vocal Subtitle and Kinetic Lyrics Generator.

Generates center-screen (.ass) timed lyrics subtitles in target language script
with autonomous font management, beat synchronization, and SRT/VTT exports.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any
import imageio_ffmpeg

from src.core.telemetry import logger
from src.scripts.local_subtitles import generate_kinetic_ass


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
    min_intro = 6.0
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
                    min_intro = max(5.0, min(10.0, float(grid.drop_timestamps[0])))
                    logger.info(f"vocal_onset_detected: {min_intro:.2f}s using LocalBeatDetector")
        except Exception as e:
            logger.warning(f"beat_detection_failed_fallback: {e}")

    if segments and segments[0]["start"] < min_intro:
        shift = min_intro - segments[0]["start"]
        for s in segments:
            s["start"] = round(min(total_duration - 1.0, s["start"] + shift), 2)
            s["end"] = round(min(total_duration, s["end"] + shift), 2)
    elif not segments:
        import re
        raw_lyrics = str(storyboard_data.get("lyrics") or "")
        # Remove bracketed section tags like [Hook], [Verse 1], etc.
        cleaned_lyrics = re.sub(r"\[.*?\]", "\n", raw_lyrics)
        # Split on newlines, exclamation marks, or commas followed by space
        raw_phrases = [p.strip() for p in re.split(r"[\n\r!]+", cleaned_lyrics) if p.strip()]
        lines = raw_phrases or [storyboard_data.get("title_localized") or storyboard_data.get("title_en") or ""]
        tpl = max(3.5, (total_duration - min_intro) / max(1, len(lines)))
        curr = min_intro
        for l in lines:
            end_t = min(total_duration, curr + tpl)
            segments.append({"start": round(curr, 2), "end": round(end_t, 2), "text": l})
            curr = end_t
    sub_file = generate_kinetic_ass(segments=segments, output_path=out_ass_path, language=language, font_size=42, alignment=2, font_name=font_name)
    try:
        from src.scripts.local_subtitles import generate_srt, generate_vtt
        en_segs = [{"start": float(s["start"]), "end": min(total_duration, float(s["end"])), "text": str(s.get("text_en") or s.get("text")).strip()} for s in raw_segs if isinstance(s, dict)] or segments
        generate_srt(segments=en_segs, output_path=out_ass_path.parent / "captions_en.srt")
        generate_vtt(segments=en_segs, output_path=out_ass_path.parent / "captions_en.vtt")
        generate_srt(segments=segments, output_path=out_ass_path.parent / f"captions_{language}.srt")
        generate_vtt(segments=segments, output_path=out_ass_path.parent / f"captions_{language}.vtt")
    except Exception as e:
        logger.warning(f"failed_generating_youtube_cc_files: {e}")

    return sub_file, fonts_dir
