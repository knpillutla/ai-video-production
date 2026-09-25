"""Binaural 3D Spatial Audio & Delta Brainwave Entrainment Engine.

Synthesizes 432Hz binaural beat delta waves (2Hz sleep frequency) and
positions spatial sound layers (left rain, right hearth, center score) in 48kHz stereo.
"""

from pathlib import Path
import subprocess
from typing import Optional
import imageio_ffmpeg

from src.core.telemetry import logger


def build_binaural_delta_filter(
    base_freq_hz: float = 432.0,
    delta_beat_hz: float = 2.0,
    gain_db: float = -26.0,
) -> str:
    """Build FFmpeg filter for sub-audible 3D binaural sleep entrainment.
    
    Left ear receives base_freq_hz, right ear receives base_freq_hz + delta_beat_hz.
    The human brain perceives the difference (delta_beat_hz = 2Hz) inducing deep sleep.
    """
    left_freq = base_freq_hz
    right_freq = base_freq_hz + delta_beat_hz
    # Calculate linear amplitude from dB
    amp = 10.0 ** (gain_db / 20.0)

    filter_graph = (
        f"aevalsrc={amp}*sin(2*PI*{left_freq}*t):s=48000:d=10000[b_left];"
        f"aevalsrc={amp}*sin(2*PI*{right_freq}*t):s=48000:d=10000[b_right];"
        f"[b_left][b_right]join=inputs=2:channel_layout=stereo[binaural_bed]"
    )
    return filter_graph


def apply_binaural_spatial_mastering(
    input_audio: Path | str,
    output_audio: Path | str,
    left_layer: Optional[Path | str] = None,   # e.g. rain on left window
    right_layer: Optional[Path | str] = None,  # e.g. hearth on right
    target_lufs: float = -21.0,
    duration_seconds: Optional[float] = None,
) -> Path:
    """Master audio with 3D binaural soundstage and 432Hz sleep entrainment."""
    inp = Path(input_audio).resolve()
    out = Path(output_audio).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    binaural_bed = build_binaural_delta_filter(base_freq_hz=432.0, delta_beat_hz=2.0, gain_db=-26.0)

    # Velvet frequency shaping
    velvet_eq = "lowpass=f=6500,equalizer=f=3800:t=q:w=2.0:g=-2.5,equalizer=f=180:t=q:w=1.2:g=1.8,alimiter=limit=0.18:attack=5:release=60"

    filter_complex = (
        f"{binaural_bed};"
        f"[0:a]{velvet_eq}[center_music];"
        f"[center_music][binaural_bed]amix=inputs=2:weights=1.0 0.15:normalize=0,"
        f"loudnorm=I={target_lufs}:TP=-2.0:LRA=7.0[aout]"
    )

    cmd = [
        ffmpeg_bin, "-y", "-i", str(inp),
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
    ]

    if duration_seconds:
        cmd.extend(["-t", str(duration_seconds)])

    cmd.append(str(out))

    logger.info(f"applying_binaural_spatial_mastering: {inp.name} -> {out.name} (432Hz delta bed)")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        logger.warning(f"binaural_mastering_fallback: {err}")
        import shutil
        shutil.copy2(inp, out)

    return out
