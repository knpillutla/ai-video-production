"""Reusable Directorial Pacing and Narrative Rhythm Curve Engine."""


def calculate_scene_durations(total_duration: float, num_scenes: int, genre: str = "comedy", curve_type: str = "auto") -> list[float]:
    """Calculate dynamically paced scene durations according to cinematic narrative tension curves."""
    if num_scenes <= 0 or total_duration <= 0:
        return []
    if num_scenes == 1:
        return [round(total_duration, 2)]

    g_low = genre.lower()

    if "walk" in g_low or "tour" in g_low or "scenic" in g_low:
        # Tranquil balanced cadence (e.g. 5.0s, 5.0s, 5.0s)
        base = round(total_duration / num_scenes, 2)
        durations = [base] * num_scenes
        durations[-1] = round(total_duration - sum(durations[:-1]), 2)
        return durations

    if any(k in g_low for k in ("dance", "music", "teenmaar", "folk")):
        # Musical Beat Cadence: Longer intro groove -> Medium verse -> Rapid hook cuts
        weights = [1.2, 1.0, 0.8, 0.7][:num_scenes]
        while len(weights) < num_scenes:
            weights.append(0.7)
        tot_w = sum(weights)
        durations = [round((w / tot_w) * total_duration, 2) for w in weights]
        durations[-1] = round(total_duration - sum(durations[:-1]), 2)
        return durations

    # Three-Act Dramatic Build (Establishing Wide -> Rising Tension -> Climax -> Resolution)
    if num_scenes >= 4:
        weights = [1.3, 1.1, 0.7, 0.9][:num_scenes]
        tot_w = sum(weights)
        durations = [round((w / tot_w) * total_duration, 2) for w in weights]
        durations[-1] = round(total_duration - sum(durations[:-1]), 2)
        return durations

    base = round(total_duration / num_scenes, 2)
    durations = [base] * num_scenes
    durations[-1] = round(total_duration - sum(durations[:-1]), 2)
    return durations


__all__ = ["calculate_scene_durations"]
