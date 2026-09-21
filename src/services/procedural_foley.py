"""Procedural Multi-Track Foley and Atmospheric ASMR Sound Synthesizer.

Synthesizes high-fidelity 48kHz stereo environmental audio stems (rain, wind, footsteps,
room tone) using deterministic procedural DSP math with zero external audio assets.
"""

import math
from pathlib import Path
import random
import struct
import wave


def _generate_pink_noise(num_samples: int, seed: int = 42) -> list[float]:
    """Generate filtered pink noise for natural weather and wind simulation."""
    rng = random.Random(seed)
    white = [rng.uniform(-1.0, 1.0) for _ in range(num_samples)]
    pink = [0.0] * num_samples
    b0 = b1 = b2 = b3 = b4 = b5 = b6 = 0.0
    for i, w in enumerate(white):
        b0 = 0.99886 * b0 + w * 0.0555179
        b1 = 0.99332 * b1 + w * 0.0750759
        b2 = 0.96900 * b2 + w * 0.1538520
        b3 = 0.86650 * b3 + w * 0.3104856
        b4 = 0.55000 * b4 + w * 0.5329522
        b5 = -0.7616 * b5 - w * 0.0168980
        pink[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11
        b6 = w * 0.115926
    return pink


def synthesize_foley_stem(
    weather_type: str,
    setting_type: str,
    space: str,
    duration_seconds: float,
    output_path: Path | str,
    sample_rate: int = 48000,
) -> Path:
    """Synthesize a continuous 48kHz stereo atmospheric foley audio file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    num_samples = int(duration_seconds * sample_rate)
    left_channel = [0.0] * num_samples
    right_channel = [0.0] * num_samples

    w_lower = (weather_type or "").lower()
    s_lower = (setting_type or "").lower()
    is_indoor = (space or "").lower() == "indoor"

    # 1. Weather Layer Synthesis
    if any(k in w_lower for k in ("rain", "monsoon", "downpour", "drizzle", "storm")):
        noise = _generate_pink_noise(num_samples, seed=101)
        rain_gain = 0.35 if "heavy" in w_lower or "downpour" in w_lower else 0.18
        if is_indoor:
            rain_gain *= 0.30  # Muted through windows
        rng = random.Random(202)
        for i in range(num_samples):
            n = noise[i] * rain_gain
            # Add sporadic droplet clicks
            if rng.random() < (0.015 if "heavy" in w_lower else 0.006):
                click = rng.uniform(-0.6, 0.6) * (0.4 if is_indoor else 0.85)
                n += click
            left_channel[i] += n * 0.95
            right_channel[i] += n * 1.05
    elif any(k in w_lower for k in ("snow", "blizzard", "arctic", "winter")):
        noise = _generate_pink_noise(num_samples, seed=303)
        wind_gain = 0.28 if "blizzard" in w_lower else 0.12
        if is_indoor:
            wind_gain *= 0.25
        for i in range(num_samples):
            t = i / sample_rate
            gust = 1.0 + 0.45 * math.sin(2 * math.pi * 0.18 * t) * math.cos(2 * math.pi * 0.07 * t)
            n = noise[i] * wind_gain * gust
            left_channel[i] += n
            right_channel[i] += n * 0.90
    else:
        # Subtle ambient room tone / daylight breeze
        noise = _generate_pink_noise(num_samples, seed=404)
        base_gain = 0.04 if is_indoor else 0.08
        for i in range(num_samples):
            left_channel[i] += noise[i] * base_gain
            right_channel[i] += noise[i] * base_gain

    # 2. Footstep Cadence Layer (for walking tours and street scenes)
    if "walk" in s_lower or "tour" in s_lower or "street" in s_lower:
        step_interval = int(sample_rate * 0.62)  # ~1.6 steps per second
        step_len = int(sample_rate * 0.08)       # 80ms impact transient
        rng_step = random.Random(505)
        for start_idx in range(int(sample_rate * 0.3), num_samples - step_len, step_interval):
            side = rng_step.choice(["left", "right"])
            for j in range(step_len):
                idx = start_idx + j
                decay = math.exp(-j / (sample_rate * 0.02))
                impact = rng_step.uniform(-0.25, 0.25) * decay
                if "rain" in w_lower:
                    impact *= 1.3  # Puddle slosh accent
                if side == "left":
                    left_channel[idx] += impact * 0.7
                    right_channel[idx] += impact * 0.3
                else:
                    left_channel[idx] += impact * 0.3
                    right_channel[idx] += impact * 0.7

    # 3. Write 16-bit PCM Stereo WAV file
    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        raw_bytes = bytearray()
        for i in range(num_samples):
            clamped_l = max(-1.0, min(1.0, left_channel[i]))
            clamped_r = max(-1.0, min(1.0, right_channel[i]))
            val_l = int(clamped_l * 32767)
            val_r = int(clamped_r * 32767)
            raw_bytes.extend(struct.pack("<hh", val_l, val_r))
        wf.writeframes(raw_bytes)

    return out


__all__ = ["synthesize_foley_stem"]
