"""Procedural Visual FX and Animation Choreography for Vocal Music Videos.

Generates broadcast-grade atmospheric particle loops (petals, fireflies, light leaks, bokeh)
and compiles single-pass FFmpeg timeline filter graphs driven by Gemini's animation cues.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any
import numpy as np

from src.core.telemetry import logger
from src.compositor.vocal_overlay_particles import ensure_fx_overlay, FX_CACHE_DIR


def resolve_scene_vfx_type(
    theme: str | None = None,
    timeline_cues: list[dict[str, Any]] | None = None,
    setting: str | None = None,
) -> str:
    """Resolve an authentic atmospheric visual effect matching the scene environment."""
    t_low = f"{theme or ''} {setting or ''}".lower()
    if any(k in t_low for k in ("snow", "alps", "mountain", "winter", "glacier", "blizzard", "frost", "ice")):
        return "alpine_snow_crystals"
    if any(k in t_low for k in ("rain", "monsoon", "storm", "droplet", "mist")):
        return "monsoon_rain_mist"
    if any(k in t_low for k in ("cafe", "bistro", "candle", "night", "twilight", "evening", "urban", "jazz")):
        return "romantic_bokeh_drift"
    if any(k in t_low for k in ("sun", "daylight", "golden hour", "beach", "summer")):
        return "sunlight_lens_leak"
    if any(k in t_low for k in ("fire", "campfire", "hearth", "embers", "woods")):
        return "golden_fireflies"
    if any(k in t_low for k in ("flower", "garden", "blossom", "spring", "festiv", "dussera", "dussehra", "diwali", "jathara", "celebrat", "carnival")):
        return "floating_petals_down"

    if timeline_cues:
        for cue in timeline_cues:
            eff = cue.get("effect_type")
            if eff in ("shimmering_sparkles", "golden_fireflies", "romantic_bokeh_drift", "floating_petals_down", "floating_petals_up", "monsoon_rain_mist", "alpine_snow_crystals", "sunlight_lens_leak"):
                return eff

    return "shimmering_sparkles"


def _build_crossfade_filter(
    count: int, total_duration: float, segment_durations: list[float] | None = None, fps: int = 30,
    enable_movement: bool = False, scene_movements: list[str] | None = None, is_mass: bool = False,
    scene_speeds: list[str] | None = None,
) -> tuple[list[str], str]:
    if not enable_movement:
        if count <= 1:
            return [f"[0:v]scale=3840:2160,fps={fps},format=yuv420p,setsar=1[base]"], "base"
        chains = [f"[{i}:v]scale=3840:2160,fps={fps},format=yuv420p,setsar=1[v_seg_{i}]" for i in range(count)]
    else:
        chains = []
        for i in range(count):
            dur = segment_durations[i] if segment_durations and i < len(segment_durations) else (total_duration / count)
            d_frames = max(30, int(dur * fps))
            mov = (scene_movements[i] if scene_movements and i < len(scene_movements) else "").lower().strip()
            spd = (scene_speeds[i] if scene_speeds and i < len(scene_speeds) else "").lower().strip()
            if not mov: mov = ["dollyin", "tilt-up", "pan-right", "orbit-left", "dollyout"][i % 5]
            tag = "base" if count <= 1 else f"v_seg_{i}"
            # Scene 0 (intro title card slide) must never have motion (static canvas during orchestral intro)
            if i == 0 or any(w in mov for w in ("stay", "hold", "static", "fixed", "motion", "video")) or spd == "steady":
                chains.append(f"[{i}:v]scale=3840:2160:flags=lanczos,fps={fps},format=yuv420p,setsar=1[{tag}]"); continue

            if is_mass or spd == "fast" or any(k in mov for k in ("crash", "punch", "snap", "drop")):
                w_b = 6.283 / max(45, int(fps * (2.4 if spd == "fast" else 3.4)))
                is_out = any(k in mov for k in ("dollyout", "zoomout", "pull"))
                z_e = f"{1.11 if is_out else 1.03}{'-' if is_out else '+'}0.07*(0.5-0.5*cos(on*{w_b:.4f})){'-' if is_out else '+'}0.02*abs(sin(on*0.44))"
                x_e = f"'(iw-iw/zoom)*(0.5+{'-' if 'left' in mov else ''}0.42*sin(on*{w_b:.4f}))'" if any(k in mov for k in ("pan", "orbit", "swirl", "left", "right")) else "'iw/2-(iw/zoom/2)'"
                y_e = f"'(ih-ih/zoom)*(0.5+{'-' if any(k in mov for k in ('up', 'crane')) else ''}0.38*cos(on*{w_b:.4f}))'" if any(k in mov for k in ("tilt", "crane", "pedestal", "up", "down")) else "'ih/2-(ih/zoom/2)'"
            else:
                z_mag = 0.06 if spd == "slow" else 0.10
                if any(k in mov for k in ("dollyout", "zoomout", "pull")): z_e = f"{1.0 + z_mag:.2f}-{z_mag:.2f}*(on/{d_frames})"
                elif any(k in mov for k in ("dollyin", "zoomin", "push")): z_e = f"1.0+{z_mag:.2f}*(on/{d_frames})"
                elif "orbit" in mov or "swirl" in mov: z_e = f"1.05+{z_mag*0.5:.2f}*sin(on/{d_frames}*3.14)"
                else: z_e = "1.06"
                x_e = f"'(iw-iw/zoom)*(1.0-on/{d_frames})'" if any(k in mov for k in ("left", "pan-left")) else (f"'(iw-iw/zoom)*(on/{d_frames})'" if any(k in mov for k in ("right", "pan-right", "orbit", "swirl")) else "'iw/2-(iw/zoom/2)'")
                y_e = f"'(ih-ih/zoom)*(1.0-on/{d_frames})'" if any(k in mov for k in ("up", "tilt-up", "pedestal", "crane")) else (f"'(ih-ih/zoom)*(on/{d_frames})'" if any(k in mov for k in ("down", "tilt-down")) else "'ih/2-(ih/zoom/2)'")
            chains.append(f"[{i}:v]zoompan=z='{z_e}':x={x_e}:y={y_e}:d={d_frames}:s=3840x2160:fps={fps},format=yuv420p,setsar=1[{tag}]")
        if count <= 1: return chains, "base"

    prev, cum_time = "v_seg_0", 0.0
    for k in range(1, count):
        seg_dur = segment_durations[k - 1] if segment_durations and k - 1 < len(segment_durations) else (total_duration / count)
        fade_dur = min(1.2, max(0.6, seg_dur * 0.12))
        cum_time += seg_dur
        offset = max(0.1, cum_time - fade_dur)
        out_s = "base" if k == count - 1 else f"xf_{k}"
        chains.append(f"[{prev}][v_seg_{k}]xfade=transition=fade:duration={fade_dur:.2f}:offset={offset:.2f}[{out_s}]")
        prev = out_s
    return chains, "base"


def compile_vocal_base_filter_complex(
    image_count: int, total_duration: float, sub_path: Path | None = None,
    fonts_dir: Path | str | None = None, fps: int = 30, segment_durations: list[float] | None = None,
    enable_movement: bool = False, scene_movements: list[str] | None = None, is_mass: bool = False,
    scene_speeds: list[str] | None = None,
) -> str:
    """Compile Stage 1 base filter complex: image crossfades + subtitles + 48k audio."""
    count = max(1, image_count)
    filter_chains, current_stream = _build_crossfade_filter(count, total_duration, segment_durations=segment_durations, fps=fps, enable_movement=enable_movement, scene_movements=scene_movements, is_mass=is_mass, scene_speeds=scene_speeds)
    if sub_path and sub_path.is_file():
        clean_sub = sub_path.resolve().as_posix().replace(":", r"\\:")
        clean_font = f":fontsdir={Path(fonts_dir).resolve().as_posix().replace(':', r'\\:')}" if fonts_dir and Path(fonts_dir).is_dir() else ""
        filter_chains.append(f"[{current_stream}]subtitles=filename={clean_sub}{clean_font}[v_out]")
    else: filter_chains.append(f"[{current_stream}]null[v_out]")
    filter_chains.append(f"[{count}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a_out]")
    return ";".join(filter_chains)


def compile_vocal_filter_complex(
    timeline_cues: list[dict[str, Any]], total_duration: float, sub_path: Path | None = None,
    fps: int = 30, fonts_dir: Path | str | None = None, image_count: int = 1,
    enable_overlays: bool | None = None, fast_glide: bool = False, static_canvas: bool = True,
    enable_loudnorm: bool = True, fx_type: str = "shimmering_sparkles", seed: int = 0,
) -> tuple[list[str], str]:
    eff_overlays = enable_overlays if enable_overlays is not None else True
    count = max(1, image_count)
    filter_chains, current_stream = _build_crossfade_filter(count, total_duration, fps=fps)
    extra_args: list[str] = []
    if eff_overlays:
        overlay_clip = ensure_fx_overlay(fx_type, seed=seed)
        extra_args.extend(["-stream_loop", "-1", "-i", str(overlay_clip.resolve())])
        filter_chains.append(f"[{count + 1}:v]colorkey=0x000000:0.04:0.12,format=yuva420p,scale=3840:2160:flags=fast_bilinear[fx_alpha]")
        filter_chains.append(f"[{current_stream}][fx_alpha]overlay=x=0:y=0:format=auto[m_fx]")
        current_stream = "m_fx"
    if sub_path and sub_path.is_file():
        clean_sub = sub_path.resolve().as_posix().replace(":", r"\\:")
        clean_font = f":fontsdir={Path(fonts_dir).resolve().as_posix().replace(':', r'\\:')}" if fonts_dir and Path(fonts_dir).is_dir() else ""
        filter_chains.append(f"[{current_stream}]subtitles=filename={clean_sub}{clean_font}[v_out]")
    else: filter_chains.append(f"[{current_stream}]null[v_out]")
    a_f = "loudnorm=I=-14.0:TP=-1.0:LRA=7.0" if enable_loudnorm else "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
    filter_chains.append(f"[{count}:a]{a_f}[a_out]")
    return extra_args, ";".join(filter_chains)




