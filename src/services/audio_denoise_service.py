"""Spectral Audio De-noising & Noise Stem Separation Service.

Separates background hiss, diffusion noise, and simulated wind artifacts from Suno tracks.
Outputs a crystal-clear acoustic soundtrack and an isolated noise residual stem (.wav).
"""

from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import imageio_ffmpeg

from src.core.telemetry import logger


def separate_and_denoise_soundtrack(
    input_audio: Path | str,
    clean_output: Path | str,
    noise_stem_output: Optional[Path | str] = None,
    strength: float = 1.0,
    force_rerun: bool = False,
) -> Tuple[Path, Optional[Path]]:
    """Separate audio into clean acoustic master and isolated noise residual stem.
    
    Uses non-local means audio denoising (anlmdn) and phase-inverted subtraction
    to cleanly extract background diffusion hiss and stationary noise.
    """
    inp = Path(input_audio).resolve()
    out_clean = Path(clean_output).resolve()
    out_noise = Path(noise_stem_output).resolve() if noise_stem_output else None

    if not inp.is_file():
        raise FileNotFoundError(f"Input soundtrack not found: {inp}")

    if not force_rerun and out_clean.is_file() and out_clean.stat().st_size > 1000:
        if not out_noise or (out_noise.is_file() and out_noise.stat().st_size > 1000):
            logger.info(f"decision_audio_denoise_cache_hit: Reusing {out_clean.name} ($0.00 spend)")
            return out_clean, out_noise

    out_clean.parent.mkdir(parents=True, exist_ok=True)
    if out_noise:
        out_noise.parent.mkdir(parents=True, exist_ok=True)

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()

    # Calibrated Non-Local Means Denoiser parameters:
    # s=7 (smoothness/patch radius), p=0.003 (noise patch threshold), r=0.006 (research radius)
    smooth_factor = max(4, min(12, int(7 * strength)))
    p_val = 0.003 * strength
    r_val = 0.006 * strength

    denoise_filter = f"highpass=f=35,anlmdn=s={smooth_factor}:p={p_val:.4f}:r={r_val:.4f}:m=15"

    if out_noise:
        # Split original audio into 2 streams, denoise stream 2, split cleaned stream,
        # then subtract cleaned from original using 180-degree phase cancellation (amix weights 1 -1)
        filter_complex = (
            f"[0:a]asplit=2[orig][to_denoise];"
            f"[to_denoise]{denoise_filter}[clean_tmp];"
            f"[clean_tmp]asplit=2[cleaned][clean_for_mix];"
            f"[orig][clean_for_mix]amix=inputs=2:weights=1 -1:normalize=0[noise_stem]"
        )
        cmd = [
            ffmpeg_bin, "-y", "-i", str(inp),
            "-filter_complex", filter_complex,
            "-map", "[cleaned]", "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000", str(out_clean),
            "-map", "[noise_stem]", "-c:a", "pcm_s16le", "-ar", "48000", str(out_noise),
        ]
    else:
        cmd = [
            ffmpeg_bin, "-y", "-i", str(inp),
            "-af", denoise_filter,
            "-c:a", "libmp3lame", "-b:a", "320k", "-ar", "48000", str(out_clean),
        ]

    logger.info(f"denoising_soundtrack: {inp.name} -> {out_clean.name} (noise_stem={bool(out_noise)})")
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as err:
        err_msg = (err.stderr or err.stdout or str(err)).strip()
        logger.warning(f"audio_denoising_failed_fallback: {err_msg}")
        import shutil
        shutil.copy2(inp, out_clean)
        return out_clean, None

    return out_clean, out_noise
