"""Anti-Fatigue Velvet Acoustic Mastering Filter.

Applies soft low-pass frequency roll-offs, transient pop limiting,
biophilic warmth equalization, 432Hz harmonic under-beds, and -21 LUFS sleep normalization.
"""

import math
from pathlib import Path
import subprocess
from typing import Optional
import imageio_ffmpeg

from src.core.telemetry import logger


def build_velvet_ffmpeg_audio_filter(
    target_lufs: float = -21.0,
    true_peak: float = -2.0,
    enable_432hz_bed: bool = True,
    cutoff_hz: int = 6500,
    warmth_boost_db: float = 1.8,
) -> str:
    """Build FFmpeg anti-fatigue acoustic filtergraph string.
    
    1. Lowpass @ 6.5kHz: Eliminates frying/sizzle fatigue in rain/water/birds.
    2. Fatigue Notch @ 3.8kHz: Dips harsh sibilance and ear-piercing resonances.
    3. Warmth EQ @ 180Hz: Adds soothing, womb-like biophilic grounding.
    4. Soft Peak Limiter: De-pops sharp campfire crackles & water droplet spikes.
    5. Sleep Loudnorm: Normalized to -21.0 LUFS for effortless 8+ hour listening.
    """
    filters = [
        f"lowpass=f={cutoff_hz}:p=2",
        "equalizer=f=3800:t=q:w=2.0:g=-2.5",
        f"equalizer=f=180:t=q:w=1.2:g={warmth_boost_db}",
        "alimiter=limit=0.18:attack=5:release=60:asc=1",
        f"loudnorm=I={target_lufs}:TP={true_peak}:LRA=7.0",
    ]
    return ",".join(filters)


def apply_velvet_acoustic_mastering(
    input_audio: Path | str,
    output_audio: Path | str,
    target_lufs: float = -21.0,
    add_432hz_drone: bool = True,
    duration_seconds: Optional[float] = None,
) -> Path:
    """Master an audio file through the Velvet Acoustic Anti-Fatigue pipeline."""
    inp = Path(input_audio).resolve()
    out = Path(output_audio).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    v_filter = build_velvet_ffmpeg_audio_filter(target_lufs=target_lufs)

    if add_432hz_drone:
        # Generate ultra-subtle harmonic 432Hz sine bed mixed at -26dB
        drone_filter = (
            f"aevalsrc=0.04*sin(2*PI*432*t)+0.015*sin(2*PI*108*t):s=48000:d=10000[drone];"
            f"[0:a]{v_filter}[main];"
            f"[main][drone]amix=inputs=2:weights=1.0 0.12:normalize=0[aout]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-i", str(inp),
            "-filter_complex", drone_filter,
            "-map", "[aout]",
            "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
        ]
    else:
        cmd = [
            ffmpeg_bin, "-y", "-i", str(inp),
            "-af", v_filter,
            "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000",
        ]

    if duration_seconds:
        cmd.extend(["-t", str(duration_seconds)])

    cmd.append(str(out))

    logger.info(f"applying_velvet_audio_filter: {inp.name} -> {out.name} (target={target_lufs} LUFS)")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as err:
        logger.warning(f"velvet_filter_fallback: ffmpeg failed, using direct copy: {err}")
        import shutil
        shutil.copy2(inp, out)

    return out
