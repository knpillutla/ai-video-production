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

FX_CACHE_DIR = Path("storage/_fx_cache")


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


def ensure_fx_overlay(
    fx_type: str, seed: int = 0, width: int = 1920, height: int = 1080, fps: int = 30
) -> Path:
    """Ensure a seamless 20-second continuous procedural atmospheric loop with harmonic periodicity."""
    FX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    norm_seed = abs(seed) % 30
    out_path = FX_CACHE_DIR / f"{fx_type}_s{norm_seed}_v6.mp4"
    if out_path.is_file() and out_path.stat().st_size > 1000:
        return out_path

    import cv2
    frames = 600  # 20 seconds at 30 fps for natural musical phrasing
    vw = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    rng = np.random.RandomState((abs(hash(fx_type)) + norm_seed * 17929) % (2**31 - 1))

    if fx_type == "alpine_snow_crystals":
        n = 60
        x0, y0 = rng.uniform(0, width, n), rng.uniform(0, height, n)
        r_base, wraps = rng.uniform(2.0, 5.5, n), rng.randint(2, 6, n)
        vy = wraps * (height + 40) / frames
        tw_omega = 2.0 * math.pi * rng.randint(4, 14, n) / frames
        phi = rng.uniform(0, 2.0 * math.pi, n)
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            cy_arr = (y0 + vy * f) % (height + 40) - 20
            cx_arr = (x0 + np.sin(phi + f * (2.0 * math.pi * 2 / frames)) * 15) % width
            tw_arr = np.sin(f * tw_omega + phi) ** 2
            for i in range(n):
                rad = max(1, int(r_base[i] * (0.8 + 0.4 * tw_arr[i])))
                cx, cy = int(cx_arr[i]), int(cy_arr[i])
                cv2.circle(canvas, (cx, cy), rad, (255, 255, 255), -1)
                if tw_arr[i] > 0.4 and rad > 2:
                    glim = int(rad * 2.0)
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (245, 235, 215), 1)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (245, 235, 215), 1)
            vw.write(canvas)

    elif fx_type == "sunlight_lens_leak":
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pulse = 0.5 + 0.5 * math.sin(2.0 * math.pi * 4 * f / frames + norm_seed)
            cx = int(width * 0.25 + 60 * math.sin(2.0 * math.pi * 2 * f / frames))
            cy = int(height * 0.3)
            axes = (int(320 + 80 * pulse), int(120 + 40 * pulse))
            cv2.ellipse(canvas, (cx, cy), axes, 15, 0, 360, (20, 110, 210), -1)
            cv2.ellipse(canvas, (cx + 80, cy + 40), (int(axes[0] * 0.6), int(axes[1] * 0.6)), -10, 0, 360, (40, 160, 240), -1)
            vw.write(canvas)

    elif fx_type == "monsoon_rain_mist":
        n = 80
        x0, y0 = rng.uniform(0, width, n), rng.uniform(0, height, n)
        wraps, lengths = rng.randint(8, 18, n), rng.uniform(10, 22, n)
        vy = wraps * (height + 60) / frames
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            cy_arr = (y0 + vy * f) % (height + 60) - 30
            cx_arr = (x0 - 2.0 * (f % (width / 2.0))) % width
            for i in range(n):
                cx, cy = int(cx_arr[i]), int(cy_arr[i])
                cv2.line(canvas, (cx, cy), (cx - 2, cy + int(lengths[i])), (200, 215, 220), 1)
            vw.write(canvas)

    elif fx_type in ("vocal_decorators", "floating_petals_up", "floating_petals_down", "festive_flower_swirl"):
        n_p, n_s = 18, 36
        px, py = rng.uniform(0.05 * width, 0.95 * width, n_p), rng.uniform(-60, -10, n_p)
        drift_x, drift_y = rng.uniform(-0.12 * width, 0.12 * width, n_p), rng.uniform(0.9 * height, 1.25 * height, n_p)
        r_base = rng.uniform(3.0, 7.5, n_p)
        lifespans, offsets = rng.choice([480, 540, 600], n_p), rng.uniform(0, 600, n_p)
        sway_amp, sway_freq, rot_speeds = rng.uniform(10.0, 20.0, n_p), 2.0 * math.pi * rng.randint(2, 5, n_p), rng.uniform(-80.0, 80.0, n_p)
        palette = [(215, 175, 255), (180, 210, 255), (70, 190, 255), (50, 150, 255), (240, 245, 255), (255, 210, 230)]
        p_colors = [palette[i % len(palette)] for i in range(n_p)]
        p_shapes = [i % 4 for i in range(n_p)]
        sx, sy = rng.uniform(40, width - 40, n_s), rng.uniform(40, height - 40, n_s)
        sr, sc = rng.uniform(2.0, 5.0, n_s), rng.randint(4, 12, n_s)
        s_omega, s_phi = 2.0 * math.pi * sc / frames, rng.uniform(0, 2.0 * math.pi, n_s)

        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            for k in range(n_s):
                tw = math.sin(f * s_omega[k] + s_phi[k]) ** 2
                if tw > 0.18:
                    rad = max(1, int(sr[k] * tw))
                    cx, cy = int(sx[k]), int(sy[k])
                    cv2.circle(canvas, (cx, cy), rad, (int(220 * tw), int(240 * tw), int(255 * tw)), -1, cv2.LINE_AA)
                    glim = int(rad * 2.2)
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (int(160 * tw), int(215 * tw), int(255 * tw)), 1, cv2.LINE_AA)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (int(160 * tw), int(215 * tw), int(255 * tw)), 1, cv2.LINE_AA)
            for i in range(n_p):
                prog = ((f + offsets[i]) % lifespans[i]) / float(lifespans[i])
                alpha = math.sin(prog * math.pi) ** 2
                if alpha < 0.05: continue
                cx = px[i] + prog * drift_x[i] + sway_amp[i] * math.sin(prog * sway_freq[i])
                cy = py[i] + prog * drift_y[i] + (sway_amp[i] * 0.3) * math.cos(prog * sway_freq[i])
                if cx < -40 or cx > width + 40 or cy < -40 or cy > height + 40: continue
                angle, bc = rot_speeds[i] * prog, p_colors[i]
                c_eff, rb, st = (int(bc[0] * alpha), int(bc[1] * alpha), int(bc[2] * alpha)), max(2, int(r_base[i])), p_shapes[i]
                pt = (int(cx), int(cy))
                if st == 0:
                    cv2.ellipse(canvas, pt, (rb, max(1, int(rb * 0.38))), int(angle), 0, 360, c_eff, -1, cv2.LINE_AA)
                elif st == 1:
                    cv2.ellipse(canvas, pt, (int(rb * 0.85), max(1, int(rb * 0.32))), int(angle - 20), 0, 360, c_eff, -1, cv2.LINE_AA)
                    cv2.ellipse(canvas, pt, (int(rb * 0.85), max(1, int(rb * 0.32))), int(angle + 20), 0, 360, c_eff, -1, cv2.LINE_AA)
                elif st == 2:
                    cv2.ellipse(canvas, pt, (int(rb * 1.1), max(1, int(rb * 0.35))), int(angle + 40), 0, 360, c_eff, -1, cv2.LINE_AA)
                else:
                    for pa in (0, 90, 180, 270):
                        cv2.ellipse(canvas, pt, (int(rb * 0.7), max(1, int(rb * 0.32))), int(angle + pa), 0, 360, c_eff, -1, cv2.LINE_AA)
                    cv2.circle(canvas, pt, max(1, int(rb * 0.22)), (int(60 * alpha), int(210 * alpha), int(255 * alpha)), -1, cv2.LINE_AA)
            vw.write(canvas)

    elif fx_type == "romantic_bokeh_drift":
        n = 24
        x0, y0 = rng.uniform(0, width, n), rng.uniform(0, height, n)
        r_base, wraps = rng.uniform(14, 32, n), rng.randint(1, 3, n)
        vx = wraps * width / frames
        pulse_omega = 2.0 * math.pi * rng.randint(2, 6, n) / frames
        phi = rng.uniform(0, 2.0 * math.pi, n)
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            cx_arr = (x0 + vx * f) % width
            cy_arr = (y0 + np.sin(phi + f * (2.0 * math.pi * 2 / frames)) * 12) % height
            pulses = 0.4 + 0.3 * np.sin(f * pulse_omega + phi)
            for i in range(n):
                rad = max(2, int(r_base[i] * pulses[i]))
                cv2.circle(canvas, (int(cx_arr[i]), int(cy_arr[i])), rad, (30, 150, 220), -1)
            vw.write(canvas)

    elif fx_type == "shimmering_sparkles":
        n = 60
        x0, y0 = rng.uniform(50, width - 50, n), rng.uniform(50, height - 50, n)
        r_base = rng.uniform(3, 8, n)
        cycles = rng.randint(4, 16, n)
        omega = 2.0 * math.pi * cycles / frames
        phi = rng.uniform(0, 2.0 * math.pi, n)
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            tw_arr = np.sin(f * omega + phi) ** 2  # smooth raised-cosine bell curve (zero pop)
            for i in range(n):
                tw = tw_arr[i]
                if tw > 0.2:
                    rad = max(1, int(r_base[i] * tw))
                    cx, cy = int(x0[i]), int(y0[i])
                    cv2.circle(canvas, (cx, cy), rad, (220, 240, 255), -1)
                    glim = int(rad * 2.8)
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (160, 215, 255), 1)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (160, 215, 255), 1)
            vw.write(canvas)

    else:
        # Default: golden_fireflies / warm motes
        n = 50
        start_x = rng.uniform(0.1 * width, 0.9 * width, n)
        r_base = rng.uniform(2.5, 6.5, n)
        lifespans = rng.choice([150, 200, 300], n)
        offsets = rng.uniform(0, 600, n)
        drift_x = rng.uniform(-150.0, 150.0, n)
        sway_amp = rng.uniform(10.0, 25.0, n)
        pulse_omega = 2.0 * math.pi * rng.randint(4, 12, n)
        phi = rng.uniform(0, 2.0 * math.pi, n)
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            for i in range(n):
                L = lifespans[i]
                prog = ((f + offsets[i]) % L) / float(L)
                alpha = math.sin(prog * math.pi) ** 2
                if alpha < 0.05:
                    continue
                cy = (height + 30) - prog * (height + 100)
                cx = (start_x[i] + prog * drift_x[i] + sway_amp[i] * math.sin(f * (2.0 * math.pi * 3 / frames) + phi[i])) % width
                pulse = 0.5 + 0.5 * math.sin(f * (pulse_omega[i] / frames) + phi[i])
                rad = max(1, int(r_base[i] * (0.8 + 0.4 * pulse)))
                c_eff = (int(40 * alpha), int(180 * alpha), int(245 * alpha))
                cv2.circle(canvas, (int(cx), int(cy)), rad, c_eff, -1)
            vw.write(canvas)

    vw.release()
    logger.info(f"generated_continuous_fx_loop: {fx_type} s{norm_seed} ({out_path.stat().st_size} bytes)")
    return out_path


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
            if any(w in mov for w in ("stay", "hold", "static", "fixed")) or spd == "steady":
                chains.append(f"[{i}:v]scale=3840:2160,fps={fps},format=yuv420p,setsar=1[{tag}]"); continue

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



