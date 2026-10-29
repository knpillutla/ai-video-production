"""Documentary Audio Mixer & Subtitle Alignment Engine.

Mixes voiceover at -14.0 LUFS with ultra-low ducked BGM (-26dB) to prevent auditory fatigue,
and auto-generates timestamped SRT subtitle tracks.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import List, Optional
import imageio_ffmpeg

from src.core.telemetry import logger


def generate_documentary_subtitles(
    scenes_narration: List[str],
    scene_durations: List[float],
    output_srt: Path,
) -> Path:
    """Generate high-readability timestamped SRT subtitles from scene narration."""
    out = output_srt.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    curr_time = 0.5  # 0.5s initial offset

    def _fmt_time(sec: float) -> str:
        h = int(sec // 3600)
        m = int((sec % 3600) // 60)
        s = int(sec % 60)
        ms = int((sec - int(sec)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    for idx, (text, dur) in enumerate(zip(scenes_narration, scene_durations), 1):
        start_sec = curr_time
        speech_dur = min(dur - 0.8, max(2.5, len(text.split()) * 0.45))
        end_sec = start_sec + speech_dur

        lines.append(str(idx))
        lines.append(f"{_fmt_time(start_sec)} --> {_fmt_time(end_sec)}")
        lines.append(text)
        lines.append("")

        curr_time += dur

    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def build_active_chapters_voice_track(ep_dir: Path, chapter_indices: List[int], chapter_target_durations: Optional[dict[int, float]] = None) -> Path:
    """Build exact chapter-aligned voice track from chapter_<idx>_raw.mp3 padded to each chapter's visual duration."""
    fallback = ep_dir / "spoken_narration.mp3"
    stems_dir = ep_dir / "narration_stems"
    if not stems_dir.is_dir() or not chapter_indices:
        return fallback
    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    stems: List[Path] = []
    seen = set()
    for c_idx in chapter_indices:
        if c_idx in seen:
            continue
        seen.add(c_idx)
        raw_p = stems_dir / f"chapter_{c_idx}_raw.mp3"
        pad_p = stems_dir / f"chapter_{c_idx}_padded.mp3"
        tgt_dur = (chapter_target_durations or {}).get(c_idx)
        if raw_p.is_file() and raw_p.stat().st_size > 500 and tgt_dur and tgt_dur > 2.0:
            aligned_p = stems_dir / f"chapter_{c_idx}_aligned.mp3"
            cmd_pad = [
                ffmpeg_bin, "-y", "-i", str(raw_p),
                "-af", f"adelay=800|800,apad=whole_dur={tgt_dur:.2f}",
                "-t", f"{tgt_dur:.2f}", "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", str(aligned_p),
            ]
            try:
                subprocess.run(cmd_pad, capture_output=True, check=True)
                stems.append(aligned_p)
                continue
            except Exception:
                pass
        cand = pad_p if pad_p.is_file() else raw_p
        if cand.is_file() and cand.stat().st_size > 500:
            stems.append(cand)
    if not stems:
        return fallback
    out_voice = ep_dir / "active_spoken_narration.mp3"
    inputs: List[str] = []
    for s in stems:
        inputs.extend(["-i", str(s)])
    n = len(stems)
    filter_str = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[aout]"
    cmd = [ffmpeg_bin, "-y", *inputs, "-filter_complex", filter_str, "-map", "[aout]", "-c:a", "libmp3lame", "-b:a", "192k", str(out_voice)]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return out_voice if out_voice.is_file() and out_voice.stat().st_size > 1000 else fallback
    except Exception:
        return fallback


def mix_documentary_audio(
    voice_path: Path,
    bgm_path: Optional[Path],
    output_mixed_audio: Path,
    target_lufs: float = -14.0,
    foley_path: Optional[Path] = None,
    sfx_path: Optional[Path] = None,
    force_rerun: bool = False,
) -> Path:
    """Mix voiceover, ducked BGM (-26dB), organic foley (-30dB), and overlay transition SFX."""
    out = output_mixed_audio.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if not force_rerun and out.is_file() and out.stat().st_size > 1000:
        if not voice_path.is_file() or out.stat().st_mtime >= voice_path.stat().st_mtime:
            return out

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    if bgm_path and bgm_path.is_file():
        has_ext_foley = bool(foley_path and foley_path.is_file())
        has_sfx = bool(sfx_path and sfx_path.is_file())

        foley_filter = "[2:a]volume=0.25[foley];" if has_ext_foley else "[2:a]volume=0.045[foley];"
        foley_input = ["-i", str(foley_path)] if has_ext_foley else [
            "-f", "lavfi", "-i", "anoisesrc=c=pink:r=48000:a=0.012,lowpass=f=900,highpass=f=100"
        ]

        sfx_input = ["-i", str(sfx_path)] if has_sfx else []
        sfx_filter = "[3:a]volume=0.75[sfx];" if has_sfx else ""
        mix_inputs = "[0:a][bgm][foley][sfx]" if has_sfx else "[0:a][bgm][foley]"
        num_inputs = 4 if has_sfx else 3

        filter_str = (
            "[1:a]volume=0.15[bgm_base];"
            "[bgm_base][0:a]sidechaincompress=threshold=0.015:ratio=14:attack=150:release=800:makeup=1.0[bgm];"
            + foley_filter
            + sfx_filter
            + f"{mix_inputs}amix=inputs={num_inputs}:duration=first:dropout_transition=2[mixed];"
            + f"[mixed]loudnorm=I={target_lufs}:TP=-1.0:LRA=7[out]"
        )
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(voice_path),
            "-i", str(bgm_path),
            *foley_input,
            *sfx_input,
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            str(out)
        ]
    else:
        filter_str = f"loudnorm=I={target_lufs}:TP=-1.0:LRA=7"
        cmd = [
            ffmpeg_bin, "-y",
            "-i", str(voice_path),
            "-af", filter_str,
            "-c:a", "aac", "-b:a", "320k", "-ar", "48000",
            str(out)
        ]

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        logger.info(f"documentary_audio_mixed: {out.name}")
    except subprocess.CalledProcessError as err:
        logger.warning(f"sidechain_ducking_failed, retrying with static ducking: {err}")
        if bgm_path and bgm_path.is_file():
            fallback_filter = (
                "[1:a]volume=0.06[bgm];"
                "[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[mixed];"
                f"[mixed]loudnorm=I={target_lufs}:TP=-1.0:LRA=7[out]"
            )
            cmd_fb = [
                ffmpeg_bin, "-y", "-i", str(voice_path), "-i", str(bgm_path),
                "-filter_complex", fallback_filter, "-map", "[out]",
                "-c:a", "aac", "-b:a", "320k", "-ar", "48000", str(out)
            ]
            try:
                subprocess.run(cmd_fb, capture_output=True, check=True)
                return out
            except Exception as fb_err:
                logger.error(f"fallback_audio_mix_failed: {fb_err}")
        import shutil
        shutil.copy(voice_path, out)

    return out
