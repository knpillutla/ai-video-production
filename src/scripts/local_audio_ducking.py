"""Tier-0 Deterministic Audio Ducking Math and FFmpeg Filter Construction."""

from dataclasses import dataclass


@dataclass
class AudioDuckingConfig:
    """Parameters for ducking background score during neural voiceover."""

    ducked_speech_dip_db: float = -18.0  # -18 dB standard YouTube broadcast dip
    pause_duck_level_db: float = -6.0  # Slight swell between speech pauses
    attack_ms: int = 200  # Fade down smoothly
    release_ms: int = 350  # Fade up smoothly
    threshold: float = 0.08  # RMS activation trigger threshold


def build_sidechain_ducking_filter(
    voice_stream: str = "[a_voice]",
    bgm_stream: str = "[a_bgm]",
    output_stream: str = "[a_ducked]",
    config: AudioDuckingConfig | None = None,
) -> str:
    """Build single-pass FFmpeg sidechaincompress filter graph.

    Ducks the BGM stream whenever speech energy is detected in the voice stream.
    """
    cfg = config or AudioDuckingConfig()
    return (
        f"{bgm_stream}{voice_stream}sidechaincompress="
        f"threshold={cfg.threshold}:"
        f"ratio=6:"
        f"attack={cfg.attack_ms}:"
        f"release={cfg.release_ms}:"
        f"makeup=1.0{output_stream}"
    )


def build_timeline_volume_expression(
    speech_intervals: list[tuple[float, float]],
    base_volume: float = 0.25,
    ducked_volume: float = 0.07,
    fade_duration: float = 0.25,
) -> str:
    """Construct an evaluation volume expression based on speech intervals.

    Used when sidechain audio stream is multiplexed or pre-calculated.
    """
    if not speech_intervals:
        return f"volume={base_volume}"

    conditions = []
    for start, end in speech_intervals:
        # Extend boundaries slightly for natural breathing space
        s = max(0.0, start - fade_duration)
        e = end + fade_duration
        conditions.append(f"between(t,{s:.2f},{e:.2f})")

    combined_cond = "+".join(conditions)
    # If t is within any speech interval, volume is ducked_volume; otherwise base_volume
    return f"volume='if(gt({combined_cond},0),{ducked_volume},{base_volume})':eval=frame"


def calculate_lufs_gain_offset(
    current_lufs: float,
    target_lufs: float = -14.0,
) -> float:
    """Compute exact dB gain adjustment needed to target YouTube standard -14 LUFS."""
    return round(target_lufs - current_lufs, 2)


__all__ = [
    "AudioDuckingConfig",
    "build_sidechain_ducking_filter",
    "build_timeline_volume_expression",
    "calculate_lufs_gain_offset",
]
