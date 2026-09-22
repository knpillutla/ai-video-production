"""Deterministic procedural DSP algorithms for weather and atmospheric soundscapes."""

import math
import random


def generate_pink_noise(num_samples: int, seed: int = 42) -> list[float]:
    """Generate Paul Kellet filtered pink noise (1/f spectral slope)."""
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


def low_pass_filter(samples: list[float], alpha: float = 0.12) -> list[float]:
    """One-pole low-pass filter to soften high-frequency hiss into warm organic texture."""
    out = [0.0] * len(samples)
    prev = 0.0
    for i, s in enumerate(samples):
        prev += alpha * (s - prev)
        out[i] = prev
    return out


def synthesize_rain_layer(
    num_samples: int,
    is_heavy: bool,
    is_indoor: bool,
    sample_rate: int = 48000,
) -> tuple[list[float], list[float]]:
    """Synthesize warm stereo rain texture with gentle droplet transients and zero digital noise."""
    raw_noise = generate_pink_noise(num_samples, seed=101)
    filtered_bed = low_pass_filter(raw_noise, alpha=0.10 if is_indoor else 0.18)
    base_gain = 0.14 if is_heavy else 0.07
    if is_indoor:
        base_gain *= 0.25

    rng = random.Random(202)
    left = [filtered_bed[i] * base_gain * 0.95 for i in range(num_samples)]
    right = [filtered_bed[i] * base_gain * 1.05 for i in range(num_samples)]

    # Generate soft organic droplet micro-envelopes (smooth decaying acoustic pings)
    drop_interval = int(sample_rate * (0.04 if is_heavy else 0.12))
    drop_len = int(sample_rate * 0.008)  # 8ms smooth transient

    for start_idx in range(0, num_samples - drop_len, drop_interval):
        if rng.random() > 0.40:
            freq = rng.uniform(850.0, 1600.0)
            amp = rng.uniform(0.015, 0.045) * (0.30 if is_indoor else 1.0)
            side = rng.choice(["l", "r", "c"])
            for j in range(drop_len):
                idx = start_idx + j
                decay = math.exp(-j / (sample_rate * 0.0025))
                osc = math.sin(2 * math.pi * freq * (j / sample_rate)) * amp * decay
                if side == "l":
                    left[idx] += osc * 0.85
                    right[idx] += osc * 0.15
                elif side == "r":
                    left[idx] += osc * 0.15
                    right[idx] += osc * 0.85
                else:
                    left[idx] += osc * 0.50
                    right[idx] += osc * 0.50

    return left, right


def synthesize_wind_layer(num_samples: int, sample_rate: int, is_blizzard: bool, is_indoor: bool) -> tuple[list[float], list[float]]:
    """Synthesize smooth swirling wind gusts and cold atmospheric breeze."""
    raw_noise = generate_pink_noise(num_samples, seed=303)
    filtered = low_pass_filter(raw_noise, alpha=0.08 if is_indoor else 0.15)
    gain = 0.16 if is_blizzard else 0.08
    if is_indoor:
        gain *= 0.25
    left, right = [0.0] * num_samples, [0.0] * num_samples
    for i in range(num_samples):
        t = i / sample_rate
        gust = 1.0 + 0.40 * math.sin(2 * math.pi * 0.18 * t) * math.cos(2 * math.pi * 0.07 * t)
        n = filtered[i] * gain * gust
        left[i] = n
        right[i] = n * 0.90
    return left, right


__all__ = ["generate_pink_noise", "synthesize_rain_layer", "synthesize_wind_layer"]

