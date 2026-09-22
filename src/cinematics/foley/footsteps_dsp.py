"""Reusable surface-aware footstep and movement foley DSP module."""

import math
import random


def synthesize_footstep_layer(
    num_samples: int,
    sample_rate: int,
    surface: str = "pavement",
    has_water: bool = False,
    is_snow: bool = False,
    pace_seconds: float = 0.62,
) -> tuple[list[float], list[float]]:
    """Synthesize rhythmic surface-aware footsteps (puddle sloshes, snow crunches, dry pavement)."""
    left, right = [0.0] * num_samples, [0.0] * num_samples
    step_interval = int(sample_rate * pace_seconds)
    step_len = int(sample_rate * 0.08)  # 80ms transient duration
    rng = random.Random(505)

    for start_idx in range(int(sample_rate * 0.3), num_samples - step_len, step_interval):
        side = rng.choice(["left", "right"])
        decay_rate = sample_rate * (0.025 if is_snow else (0.018 if has_water else 0.012))
        for j in range(step_len):
            idx = start_idx + j
            decay = math.exp(-j / decay_rate)
            impact = rng.uniform(-0.08, 0.08) * decay
            if has_water:
                impact *= 1.15  # Soft subtle splash
            elif is_snow:
                impact = (impact + rng.uniform(-0.03, 0.03)) * 0.7

            if side == "left":
                left[idx] += impact * 0.70
                right[idx] += impact * 0.30
            else:
                left[idx] += impact * 0.30
                right[idx] += impact * 0.70

    return left, right


__all__ = ["synthesize_footstep_layer"]
