"""Audio-Reactive Concert Groove Engine: Deterministic Beat & Tempo Animation.

Applies authentic concert stage movement (pendulum body sway, beat-synced head nod,
and audio-reactive energy breathing) to non-singing orchestra cuts using pure signal
processing and affine computer vision (100% local CPU, 0 API spend).
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
from typing import Optional, Union

import cv2
import numpy as np

from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary
from src.core.telemetry import logger


def extract_audio_beat_features(
    audio_path: Union[str, Path],
    duration: float,
    default_bpm: float = 128.0,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Extract BPM, beat timestamps, and normalized RMS energy envelope from audio."""
    try:
        import librosa

        y, sr = librosa.load(str(audio_path), sr=22050, mono=True, duration=duration)
        if len(y) < 1000:
            raise ValueError("Audio buffer too short")

        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo[0] if isinstance(tempo, (list, np.ndarray)) else tempo)
        if bpm <= 0 or np.isnan(bpm):
            bpm = default_bpm

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=512)[0]
        max_rms = float(np.max(rms)) if len(rms) > 0 else 1.0
        norm_rms = (rms / max_rms) if max_rms > 0 else np.zeros_like(rms)
        return bpm, beat_times, norm_rms
    except Exception as ex:
        logger.warning(f"beat_feature_extraction_fallback: {ex}")
        beat_interval = 60.0 / default_bpm
        beats = np.arange(0, duration, beat_interval)
        return default_bpm, beats, np.ones(int(duration * 40)) * 0.5


def render_concert_groove_cut(
    source_media: Union[str, Path],
    audio_path: Union[str, Path],
    output_path: Union[str, Path],
    duration_seconds: float,
    fps: int = 24,
    default_bpm: float = 128.0,
    sway_amplitude_deg: float = 1.4,
    bounce_amplitude_px: float = 8.0,
) -> bool:
    """Render an audio-reactive concert grooving cut from an image or base video."""
    source_p = Path(source_media)
    audio_p = Path(audio_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not source_p.is_file() or not audio_p.is_file():
        logger.error(f"concert_groove_missing_inputs: source={source_p.exists()} audio={audio_p.exists()}")
        return False

    bpm, beat_times, norm_rms = extract_audio_beat_features(audio_p, duration_seconds, default_bpm)
    total_frames = max(1, int(duration_seconds * fps))

    # Determine source type (video or still image)
    is_video = source_p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
    cap = cv2.VideoCapture(str(source_p)) if is_video else None
    still_img = None if is_video else cv2.imread(str(source_p))

    if still_img is not None:
        h, w = still_img.shape[:2]
    elif cap is not None and cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        logger.error(f"failed_to_open_groove_source: {source_p}")
        return False

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{w}x{h}",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-i", str(audio_p),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_p),
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not proc.stdin:
        if cap:
            cap.release()
        return False

    sway_freq = (bpm / 60.0) * 0.5  # Half-tempo natural swaying cadence
    pivot_x, pivot_y = w * 0.5, h * 0.88  # Pivot from lower torso / hips

    try:
        for f_idx in range(total_frames):
            t = f_idx / float(fps)

            # 1. Fetch current frame
            if is_video and cap:
                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        frame = np.zeros((h, w, 3), dtype=np.uint8)
            else:
                frame = still_img.copy()

            # 2. Pendulum body sway (side to side)
            angle_deg = sway_amplitude_deg * np.sin(2.0 * np.pi * sway_freq * t)
            dx = float(w * 0.010 * np.sin(2.0 * np.pi * sway_freq * t + 0.25 * np.pi))

            # 3. Downbeat bounce / humming head nod
            if len(beat_times) > 0:
                diffs = t - beat_times
                past = diffs[diffs >= 0]
                dt = past[-1] if len(past) > 0 else 999.0
                nod_dy = float(bounce_amplitude_px * np.exp(-dt / 0.15))
            else:
                nod_dy = float(bounce_amplitude_px * 0.5 * (1.0 + np.cos(2.0 * np.pi * (bpm / 60.0) * t)))

            # 4. Audio energy breathing scale
            rms_idx = min(len(norm_rms) - 1, int((t / max(0.01, duration_seconds)) * len(norm_rms)))
            energy = float(norm_rms[rms_idx]) if len(norm_rms) > 0 else 0.5
            scale = 1.0 + 0.012 * energy

            # 5. Build and apply affine warp with mirrored borders to eliminate black clipping
            M = cv2.getRotationMatrix2D((pivot_x, pivot_y), angle_deg, scale)
            M[0, 2] += dx
            M[1, 2] += nod_dy
            warped = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT101)

            proc.stdin.write(warped.tobytes())
    finally:
        if cap:
            cap.release()
        if proc.stdin:
            proc.stdin.close()
        proc.wait()

    success = out_p.is_file() and out_p.stat().st_size > 10_000
    if success:
        logger.info(f"concert_groove_rendered: path={out_p.name} bpm={bpm:.1f} dur={duration_seconds}s")
    return success


__all__ = ["render_concert_groove_cut", "extract_audio_beat_features"]
