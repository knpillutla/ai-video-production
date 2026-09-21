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


def synthesize_rain_layer(num_samples: int, is_heavy: bool, is_indoor: bool) -> tuple[list[float], list[float]]:
    """Synthesize dual-channel stereo rain texture with droplet transients."""
    noise = generate_pink_noise(num_samples, seed=101)
    gain = 0.35 if is_heavy else 0.18
    if is_indoor:
        gain *= 0.30
    rng = random.Random(202)
    left, right = [0.0] * num_samples, [0.0] * num_samples
    click_prob = 0.015 if is_heavy else 0.006
    for i in range(num_samples):
        n = noise[i] * gain
        if rng.random() < click_prob:
            click = rng.uniform(-0.6, 0.6) * (0.35 if is_indoor else 0.85)
            n += click
        left[i] = n * 0.95
        right[i] = n * 1.05
    return left, right


def synthesize_wind_layer(num_samples: int, sample_rate: int, is_blizzard: bool, is_indoor: bool) -> tuple[list[float], list[float]]:
    """Synthesize swirling wind gusts and cold atmospheric breeze."""
    noise = generate_pink_noise(num_samples, seed=303)
    gain = 0.28 if is_blizzard else 0.12
    if is_indoor:
        gain *= 0.25
    left, right = [0.0] * num_samples, [0.0] * num_samples
    for i in range(num_samples):
        t = i / sample_rate
        gust = 1.0 + 0.45 * math.sin(2 * math.pi * 0.18 * t) * math.cos(2 * math.pi * 0.07 * t)
        n = noise[i] * gain * gust
        left[i] = n
        right[i] = n * 0.90
    return left, right


__all__ = ["generate_pink_noise", "synthesize_rain_layer", "synthesize_wind_layer"]
