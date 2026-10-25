"""Local Audio-Driven Movement Engine: Pitch-Responsive Head/Chin & Torso Physics.

Applies authentic concert vocal performance dynamics on 100% local CPU ($0.00 spend):
- Pitch-responsive head and chin lift during high notes/crescendo
- Half-tempo pendulum body sway around hips/torso
- Beat-locked downbeat head nod and humming dips
- Audio-reactive chest breathing expansion
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


def extract_pitch_and_energy_curves(
    audio_path: Union[str, Path],
    duration: float,
    fps: int = 24,
    default_bpm: float = 120.0,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """Extract BPM, beat times, normalized pitch curve, and normalized RMS energy."""
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

        hop = int(sr / fps)
        rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=hop)[0]
        max_r = float(np.max(rms)) if len(rms) > 0 else 1.0
        norm_rms = (rms / max_r) if max_r > 0 else np.zeros_like(rms)

        # Spectral centroid as pitch contour proxy (fast, robust on vocal mix)
        cent = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]
        min_c, max_c = float(np.min(cent)), float(np.max(cent))
        rng_c = max_c - min_c
        norm_pitch = ((cent - min_c) / (rng_c + 1e-6)) if rng_c > 0 else np.zeros_like(cent)

        # Apply temporal smoothing over ~0.75s to eliminate frame-to-frame jitter/shake
        if len(norm_pitch) > 4:
            win = min(len(norm_pitch), max(5, int(fps * 0.75)))
            if win % 2 == 0:
                win += 1
            kernel = np.hanning(win)
            k_sum = float(np.sum(kernel))
            if k_sum > 0:
                kernel = kernel / k_sum
                norm_pitch = np.convolve(norm_pitch, kernel, mode="same")
                norm_rms = np.convolve(norm_rms, kernel, mode="same")

        return bpm, beat_times, norm_rms, norm_pitch
    except Exception as ex:
        logger.warning(f"pitch_energy_curve_fallback: {ex}")
        total_f = max(1, int(duration * fps))
        beat_interval = 60.0 / default_bpm
        beats = np.arange(0, duration, beat_interval)
        return default_bpm, beats, np.ones(total_f) * 0.5, np.ones(total_f) * 0.5


def render_audio_synced_movement_cut(
    source_media: Union[str, Path],
    audio_path: Union[str, Path],
    output_path: Union[str, Path],
    duration_seconds: float,
    fps: int = 24,
    is_singing: bool = True,
    intensity: float = 0.5,
    default_bpm: float = 120.0,
    position: str = "standing",
) -> bool:
    """Render steady audio-synced pitch and tempo movement cut locally on CPU (0 model cost)."""
    source_p, audio_p, out_p = Path(source_media), Path(audio_path), Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not source_p.is_file() or not audio_p.is_file():
        logger.error(f"movement_missing_inputs: src={source_p.exists()} aud={audio_p.exists()}")
        return False

    bpm, beat_times, norm_rms, norm_pitch = extract_pitch_and_energy_curves(
        audio_p, duration_seconds, fps, default_bpm,
    )
    total_frames = max(1, int(duration_seconds * fps))

    is_video = source_p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
    cap = cv2.VideoCapture(str(source_p)) if is_video else None
    still_img = None if is_video else cv2.imread(str(source_p))

    if still_img is not None:
        h, w = still_img.shape[:2]
    elif cap is not None and cap.isOpened():
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    else:
        logger.error(f"cannot_open_movement_source: {source_p}")
        return False

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{w}x{h}", "-pix_fmt", "bgr24", "-r", str(fps),
        "-i", "-", "-i", str(audio_p),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_p),
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not proc.stdin:
        if cap: cap.release()
        return False

    is_sitting = "sit" in str(position).lower()
    sway_freq = (bpm / 60.0) * 0.5  # Half-tempo pendulum sway
    pivot_x, pivot_y = w * 0.5, (h * 0.94 if is_sitting else h * 0.88)
    sway_max_deg = (0.6 if is_sitting else 1.0) * (0.8 if is_singing else 1.0)

    try:
        for f_idx in range(total_frames):
            t = f_idx / float(fps)
            if is_video and cap:
                ret, frame = cap.read()
                if not ret or frame is None:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        frame = np.zeros((h, w, 3), dtype=np.uint8)
                # Video already contains natural living motion; pass through rock-steady
                proc.stdin.write(frame.tobytes())
                continue
            else:
                frame = still_img.copy()

            # 1. Steady pendulum torso sway (zero shaking, gentle breathing cadence)
            sway_deg = sway_max_deg * np.sin(2.0 * np.pi * sway_freq * t)
            dx = float(w * (0.003 if is_sitting else 0.005) * np.sin(2.0 * np.pi * sway_freq * t + 0.25 * np.pi))

            # 2. Smooth pitch-responsive head and chin lift during singing (zero jitter)
            idx_curve = min(f_idx, len(norm_pitch) - 1)
            pitch_val = float(norm_pitch[idx_curve]) if len(norm_pitch) > 0 else 0.5
            if is_singing:
                pitch_lift_deg = float((pitch_val - 0.4) * 0.8 * (1.0 + intensity * 0.5))
                pitch_dy = -float(h * 0.005 * (pitch_val - 0.3) * (1.0 + intensity * 0.5))
            else:
                pitch_lift_deg = 0.0
                pitch_dy = 0.0

            # 3. Audio-reactive breathing expansion (gentle continuous swell, nod_dy eliminated)
            rms_idx = min(f_idx, len(norm_rms) - 1)
            cur_rms = float(norm_rms[rms_idx]) if len(norm_rms) > 0 else 0.5
            scale = 1.0 + 0.006 * cur_rms

            total_angle = sway_deg + pitch_lift_deg
            total_dy = pitch_dy

            M = cv2.getRotationMatrix2D((pivot_x, pivot_y), total_angle, scale)
            M[0, 2] += dx
            M[1, 2] += total_dy

            warped = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT101)
            proc.stdin.write(warped.tobytes())
    finally:
        if cap: cap.release()
        if proc.stdin: proc.stdin.close()
        proc.wait()

    success = out_p.is_file() and out_p.stat().st_size > 10_000
    if success:
        logger.info(f"audio_movement_cut_rendered: path={out_p.name} singing={is_singing} bpm={bpm:.1f}")
    return success


__all__ = ["render_audio_synced_movement_cut", "extract_pitch_and_energy_curves"]
