"""Procedural Visual FX Overlay and Harmonic Particle Loops for Vocal Music Videos.

Generates 4K-ready atmospheric particle loops (petals, fireflies, light leaks, bokeh)
with mathematical harmonic periodicity for seamless looping over video backdrops.
"""

from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import cv2

from src.core.telemetry import logger

FX_CACHE_DIR = Path("storage/_fx_cache")


def ensure_fx_overlay(
    fx_type: str, seed: int = 0, width: int = 1920, height: int = 1080, fps: int = 30
) -> Path:
    """Ensure a seamless 20-second continuous procedural atmospheric loop with harmonic periodicity."""
    FX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    norm_seed = abs(seed) % 30
    out_path = FX_CACHE_DIR / f"{fx_type}_s{norm_seed}_v6.mp4"
    if out_path.is_file() and out_path.stat().st_size > 1000:
        return out_path

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
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (200, 230, 255), 1)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (200, 230, 255), 1)
            vw.write(canvas)

    elif fx_type == "monsoon_rain_mist":
        n = 120
        x0, y0 = rng.uniform(0, width, n), rng.uniform(0, height, n)
        lengths, wraps = rng.uniform(15, 35, n), rng.randint(4, 9, n)
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
                if alpha < 0.05:
                    continue
                cx = px[i] + prog * drift_x[i] + sway_amp[i] * math.sin(prog * sway_freq[i])
                cy = py[i] + prog * drift_y[i] + (sway_amp[i] * 0.3) * math.cos(prog * sway_freq[i])
                angle = rot_speeds[i] * prog * 360.0
                rb = r_base[i] * (0.85 + 0.3 * math.sin(prog * 6.28))
                col = p_colors[i]
                c_eff = (int(col[0] * alpha), int(col[1] * alpha), int(col[2] * alpha))
                pt = (int(cx % width), int(cy % (height + 80) - 40))
                st = p_shapes[i]
                if st == 0:
                    cv2.circle(canvas, pt, max(1, int(rb)), c_eff, -1, cv2.LINE_AA)
                elif st == 1:
                    cv2.ellipse(canvas, pt, (int(rb * 1.3), max(1, int(rb * 0.55))), int(angle), 0, 360, c_eff, -1, cv2.LINE_AA)
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


__all__ = ["ensure_fx_overlay", "FX_CACHE_DIR"]
