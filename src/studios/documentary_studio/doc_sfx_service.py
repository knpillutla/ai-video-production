"""Broadcast-Grade Procedural Documentary Overlay SFX Generator.

Synthesizes tactile, organic transition sound cues for on-screen documentary graphics:
- Sub-Bass Hit (48 Hz decaying sine pulse) for Chapter Slate entries
- Atmospheric Whoosh (Gaussian-filtered noise sweep) for Map & Route Insets
- Tactile UI Snap (1400 Hz dampened sine click) for Fact Badges and QR cards
Deterministic, 100% offline, $0.00 compute.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple
import wave

import numpy as np

from src.core.telemetry import logger


def generate_sub_bass_hit(duration: float = 0.6, sample_rate: int = 48000) -> np.ndarray:
    """Synthesizes a deep cinematic sub-bass rumble (48 Hz) with smooth decay."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    # 48 Hz sine with quick 8ms attack and exponential decay
    attack_samples = int(sample_rate * 0.008)
    env = np.ones(samples, dtype=np.float32)
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    env[attack_samples:] = np.exp(-5.5 * (t[attack_samples:] - t[attack_samples]))
    sig = np.sin(2.0 * np.pi * 48.0 * t) * env * 0.45
    return (sig * 32767.0).astype(np.int16)


def generate_transition_whoosh(duration: float = 0.35, sample_rate: int = 48000) -> np.ndarray:
    """Synthesizes an organic, smooth Gaussian band-limited transition whoosh."""
    samples = int(sample_rate * duration)
    t = np.linspace(-1.0, 1.0, samples, endpoint=False)
    env = np.exp(-4.5 * (t**2))  # Bell curve envelope
    noise = np.random.uniform(-1.0, 1.0, samples)
    # Moving average low-pass filter
    kernel = np.ones(12) / 12.0
    filtered = np.convolve(noise, kernel, mode="same")
    sig = filtered * env * 0.30
    return (sig * 32767.0).astype(np.int16)


def generate_ui_snap(duration: float = 0.08, sample_rate: int = 48000) -> np.ndarray:
    """Synthesizes a crisp, subtle tactile acoustic click for badge entries."""
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples, endpoint=False)
    sig = np.sin(2.0 * np.pi * 1400.0 * t) * np.exp(-42.0 * t) * 0.32
    return (sig * 32767.0).astype(np.int16)


def synthesize_overlay_sfx_track(
    total_duration: float,
    events: List[Tuple[float, str]],
    output_wav: Path,
    sample_rate: int = 48000,
) -> Path:
    """Assembles a synchronized 48kHz WAV audio track containing all overlay transition cues."""
    out = output_wav.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.is_file() and out.stat().st_size > 1000:
        return out

    total_samples = max(int(sample_rate * total_duration), sample_rate)
    track = np.zeros(total_samples, dtype=np.int32)

    for trigger_sec, sfx_type in events:
        if trigger_sec < 0 or trigger_sec >= total_duration:
            continue
        start_idx = int(trigger_sec * sample_rate)

        if sfx_type in ("sub_hit", "chapter"):
            clip = generate_sub_bass_hit(sample_rate=sample_rate)
        elif sfx_type in ("whoosh", "map", "transition"):
            clip = generate_transition_whoosh(sample_rate=sample_rate)
        elif sfx_type in ("snap", "badge", "fact", "qr"):
            clip = generate_ui_snap(sample_rate=sample_rate)
        else:
            continue

        end_idx = min(start_idx + len(clip), total_samples)
        clip_len = end_idx - start_idx
        track[start_idx:end_idx] += clip[:clip_len]

    # Clip to prevent any integer overflow and convert to 16-bit PCM
    clipped = np.clip(track, -32768, 32767).astype(np.int16)

    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(clipped.tobytes())

    logger.info(f"documentary_sfx_track_synthesized: {out.name} ({len(events)} cues, {round(total_duration, 1)}s)")
    return out


__all__ = [
    "generate_sub_bass_hit",
    "generate_transition_whoosh",
    "generate_ui_snap",
    "synthesize_overlay_sfx_track",
]
