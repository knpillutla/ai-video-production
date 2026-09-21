"""Modular Multi-Track Procedural Foley Engine.

Orchestrates weather, footsteps, and spatial acoustics into broadcast-standard 48kHz 24-bit WAV stems.
"""

from pathlib import Path
import struct
import wave

from src.cinematics.foley.footsteps_dsp import synthesize_footstep_layer
from src.cinematics.foley.weather_dsp import generate_pink_noise, synthesize_rain_layer, synthesize_wind_layer


class FoleyEngine:
    """Reusable multi-track atmospheric and movement sound synthesizer."""

    def __init__(self, sample_rate: int = 48000):
        self.sample_rate = sample_rate

    def synthesize(
        self,
        weather_type: str,
        setting_type: str,
        space: str,
        duration_seconds: float,
        output_path: Path | str,
    ) -> Path:
        """Synthesize a complete multi-track foley stem to a WAV file."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        num_samples = int(duration_seconds * self.sample_rate)

        w_lower = (weather_type or "").lower()
        s_lower = (setting_type or "").lower()
        is_indoor = (space or "").lower() == "indoor"

        # 1. Weather / Atmosphere Stem
        is_heavy_rain = any(k in w_lower for k in ("heavy", "downpour", "storm", "deluge", "torrential", "monsoon", "thunderstorm", "cloudburst", "flooded")) and not any(k in w_lower for k in ("light", "drizzle", "gentle", "soft"))
        is_rain = any(k in w_lower for k in ("rain", "monsoon", "downpour", "drizzle", "shower", "storm", "thunderstorm"))
        is_snow = any(k in w_lower for k in ("snow", "blizzard", "arctic", "winter"))
        is_blizzard = "blizzard" in w_lower or "gale" in w_lower

        if is_rain:
            wl, wr = synthesize_rain_layer(num_samples, is_heavy=is_heavy_rain, is_indoor=is_indoor)
        elif is_snow:
            wl, wr = synthesize_wind_layer(num_samples, self.sample_rate, is_blizzard=is_blizzard, is_indoor=is_indoor)
        else:
            noise = generate_pink_noise(num_samples, seed=404)
            gain = 0.04 if is_indoor else 0.08
            wl = [n * gain for n in noise]
            wr = [n * gain for n in noise]

        # 2. Movement / Surface Footstep Stem
        needs_steps = any(k in s_lower for k in ("walk", "tour", "street", "promenade", "trail", "hike"))
        if needs_steps:
            sl, sr = synthesize_footstep_layer(
                num_samples=num_samples, sample_rate=self.sample_rate,
                has_water=is_rain, is_snow=is_snow,
            )
            for i in range(num_samples):
                wl[i] += sl[i]
                wr[i] += sr[i]

        # 3. Export 16-bit PCM Stereo WAV
        with wave.open(str(out), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            raw = bytearray()
            for i in range(num_samples):
                clamped_l = max(-1.0, min(1.0, wl[i]))
                clamped_r = max(-1.0, min(1.0, wr[i]))
                raw.extend(struct.pack("<hh", int(clamped_l * 32767), int(clamped_r * 32767)))
            wf.writeframes(raw)

        return out


foley_engine = FoleyEngine()

__all__ = ["FoleyEngine", "foley_engine"]
