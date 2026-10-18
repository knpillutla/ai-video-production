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
    if any(k in t_low for k in ("flower", "garden", "blossom", "spring")):
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
    """Ensure a seamless 5-second procedural atmospheric loop exists with seed-driven variation."""
    FX_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    norm_seed = abs(seed) % 30
    out_path = FX_CACHE_DIR / f"{fx_type}_s{norm_seed}.mp4"
    if out_path.is_file() and out_path.stat().st_size > 1000:
        return out_path

    import cv2
    frames = 150  # 5 seconds at 30 fps
    vw = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    rng = np.random.RandomState((abs(hash(fx_type)) + norm_seed * 17929) % (2**31 - 1))

    if fx_type == "alpine_snow_crystals":
        n = 55
        pts = np.column_stack([
            rng.uniform(0, width, n), rng.uniform(0, height, n),
            rng.uniform(2, 6, n), rng.uniform(1.2, 3.2, n),
            rng.uniform(0, 6.28, n), rng.uniform(0.08, 0.25, n),
        ])
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pts[:, 1] += pts[:, 3]
            pts[:, 0] += np.sin(pts[:, 4] + f * 0.03) * 1.5
            pts[pts[:, 1] > height + 20, 1] = -20
            pts[pts[:, 0] < -20, 0] = width + 20
            pts[pts[:, 0] > width + 20, 0] = -20
            for p in pts:
                tw = max(0.0, math.sin(f * p[5] + p[4]))
                rad = max(1, int(p[2] * (0.8 + 0.4 * tw)))
                cx, cy = int(p[0]), int(p[1])
                cv2.circle(canvas, (cx, cy), rad, (255, 255, 255), -1)
                if tw > 0.4 and rad > 2:
                    glim = int(rad * 2.2)
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (245, 235, 215), 1)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (245, 235, 215), 1)
            vw.write(canvas)

    elif fx_type == "sunlight_lens_leak":
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pulse = 0.5 + 0.5 * math.sin(f * 0.05 + norm_seed)
            cx, cy = int(width * 0.25 + 60 * math.sin(f * 0.02)), int(height * 0.3)
            axes = (int(320 + 80 * pulse), int(120 + 40 * pulse))
            cv2.ellipse(canvas, (cx, cy), axes, 15, 0, 360, (20, 110, 210), -1)
            cv2.ellipse(canvas, (cx + 80, cy + 40), (int(axes[0]*0.6), int(axes[1]*0.6)), -10, 0, 360, (40, 160, 240), -1)
            vw.write(canvas)

    elif fx_type == "monsoon_rain_mist":
        n = 70
        pts = np.column_stack([
            rng.uniform(0, width, n), rng.uniform(0, height, n),
            rng.uniform(6.0, 14.0, n), rng.uniform(8, 18, n),
        ])
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pts[:, 1] += pts[:, 2]
            pts[:, 0] -= 1.5
            pts[pts[:, 1] > height + 30, 1] = -30
            pts[pts[:, 0] < 0, 0] = width
            for p in pts:
                cx, cy = int(p[0]), int(p[1])
                cv2.line(canvas, (cx, cy), (cx - 2, cy + int(p[3])), (200, 215, 220), 1)
            vw.write(canvas)

    elif fx_type in ("vocal_decorators", "floating_petals_up", "floating_petals_down"):
        up = fx_type != "floating_petals_down"
        n = 45
        pts = np.column_stack([
            rng.uniform(0, width, n), rng.uniform(0, height, n),
            rng.uniform(7, 18, n), rng.uniform(1.2, 3.0, n),
            rng.uniform(0, 6.28, n), rng.uniform(-45, 45, n),
            rng.uniform(0, 1, n),
        ])
        n_sp = 35 if fx_type == "vocal_decorators" else 0
        sp_pts = np.column_stack([
            rng.uniform(40, width - 40, n_sp), rng.uniform(40, height - 40, n_sp),
            rng.uniform(3, 7, n_sp), rng.uniform(0.1, 0.25, n_sp), rng.uniform(0, 6.28, n_sp),
        ]) if n_sp else None

        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            if up:
                pts[:, 1] -= pts[:, 3]
                pts[pts[:, 1] < -30, 1] = height + 20
            else:
                pts[:, 1] += pts[:, 3]
                pts[pts[:, 1] > height + 30, 1] = -20
            pts[:, 0] += np.sin(pts[:, 4] + f * 0.04) * 1.8
            for p in pts:
                center = (int(p[0]), int(p[1]))
                axes = (int(p[2]), int(p[2] * 0.55))
                angle = p[5] + math.sin(f * 0.05 + p[4]) * 20
                color = (235, 245, 255) if p[6] > 0.4 else (130, 215, 255)
                cv2.ellipse(canvas, center, axes, angle, 0, 360, color, -1)
            if sp_pts is not None:
                for sp in sp_pts:
                    tw = max(0.0, math.sin(f * sp[3] + sp[4]))
                    if tw > 0.3:
                        rad = max(1, int(sp[2] * tw))
                        cx, cy = int(sp[0]), int(sp[1])
                        cv2.circle(canvas, (cx, cy), rad, (220, 240, 255), -1)
                        glim = int(rad * 2.5)
                        cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (160, 215, 255), 1)
                        cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (160, 215, 255), 1)
            vw.write(canvas)

    elif fx_type == "romantic_bokeh_drift":
        n = 22
        pts = np.column_stack([
            rng.uniform(0, width, n), rng.uniform(0, height, n),
            rng.uniform(14, 30, n), rng.uniform(0.5, 1.4, n), rng.uniform(0, 6.28, n),
        ])
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pts[:, 0] = (pts[:, 0] + pts[:, 3]) % width
            pts[:, 1] += np.sin(pts[:, 4] + f * 0.03) * 0.6
            for p in pts:
                pulse = 0.4 + 0.3 * math.sin(f * 0.05 + p[4])
                rad = max(2, int(p[2] * pulse))
                cv2.circle(canvas, (int(p[0]), int(p[1])), rad, (30, 150, 220), -1)
            vw.write(canvas)

    elif fx_type == "shimmering_sparkles":
        n = 55
        pts = np.column_stack([
            rng.uniform(50, width - 50, n), rng.uniform(50, height - 50, n),
            rng.uniform(3, 8, n), rng.uniform(0.08, 0.22, n), rng.uniform(0, 6.28, n),
        ])
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            for p in pts:
                twinkle = max(0.0, math.sin(f * p[3] + p[4]))
                if twinkle > 0.25:
                    rad = max(1, int(p[2] * twinkle))
                    cx, cy = int(p[0]), int(p[1])
                    cv2.circle(canvas, (cx, cy), rad, (220, 240, 255), -1)
                    glim = int(rad * 2.8)
                    cv2.line(canvas, (cx - glim, cy), (cx + glim, cy), (160, 215, 255), 1)
                    cv2.line(canvas, (cx, cy - glim), (cx, cy + glim), (160, 215, 255), 1)
            vw.write(canvas)

    else:
        # Default: golden_fireflies / warm motes
        n = 45
        pts = np.column_stack([
            rng.uniform(0, width, n), rng.uniform(0, height, n),
            rng.uniform(3, 7, n), rng.uniform(1.0, 3.2, n), rng.uniform(0, 6.28, n),
        ])
        for f in range(frames):
            canvas = np.zeros((height, width, 3), dtype=np.uint8)
            pts[:, 1] -= pts[:, 3]
            pts[:, 0] += np.sin(pts[:, 4] + f * 0.05) * 1.5
            pts[pts[:, 1] < -10, 1] = height + 10
            for p in pts:
                rad = max(2, int(p[2] + np.sin(f * 0.1 + p[4]) * 1.5))
                cv2.circle(canvas, (int(p[0]), int(p[1])), rad, (40, 180, 245), -1)
            vw.write(canvas)

    vw.release()
    logger.info(f"generated_fx_overlay_loop: {fx_type} s{norm_seed} ({out_path.stat().st_size} bytes)")
    return out_path


def _build_crossfade_filter(
    count: int, total_duration: float, segment_durations: list[float] | None = None, fps: int = 30
) -> tuple[list[str], str]:
    if count <= 1:
        return [f"[0:v]scale=3840:2160,fps={fps},format=yuv420p,setsar=1[base]"], "base"
    chains = [f"[{i}:v]scale=3840:2160,fps={fps},format=yuv420p,setsar=1[v_seg_{i}]" for i in range(count)]
    prev = "v_seg_0"
    cum_time = 0.0
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
) -> str:
    """Compile Stage 1 base filter complex: image crossfades + subtitles + 48k audio."""
    count = max(1, image_count)
    filter_chains, current_stream = _build_crossfade_filter(count, total_duration, segment_durations=segment_durations, fps=fps)


    if sub_path and sub_path.is_file():
        clean_sub = sub_path.resolve().as_posix().replace(":", r"\\:")
        clean_font = f":fontsdir={Path(fonts_dir).resolve().as_posix().replace(':', r'\\:')}" if fonts_dir and Path(fonts_dir).is_dir() else ""
        filter_chains.append(f"[{current_stream}]subtitles=filename={clean_sub}{clean_font}[v_out]")
    else:
        filter_chains.append(f"[{current_stream}]null[v_out]")

    filter_chains.append(f"[{count}:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a_out]")
    return ";".join(filter_chains)


def compile_vocal_filter_complex(
    timeline_cues: list[dict[str, Any]], total_duration: float, sub_path: Path | None = None,
    fps: int = 30, fonts_dir: Path | str | None = None, image_count: int = 1,
    enable_overlays: bool | None = None, fast_glide: bool = False, static_canvas: bool = True,
    enable_loudnorm: bool = True, fx_type: str = "shimmering_sparkles", seed: int = 0,
) -> tuple[list[str], str]:
    """Single-pass filter complex using single unified decorator overlay on static tripod."""
    eff_overlays = enable_overlays if enable_overlays is not None else True
    count = max(1, image_count)
    filter_chains, current_stream = _build_crossfade_filter(count, total_duration, fps=fps)
    extra_args: list[str] = []

    if eff_overlays:
        overlay_clip = ensure_fx_overlay(fx_type, seed=seed)
        extra_args.extend(["-stream_loop", "-1", "-i", str(overlay_clip.resolve())])
        overlay_idx = count + 1
        filter_chains.append(f"[{overlay_idx}:v]colorkey=0x000000:0.04:0.12,format=yuva420p,scale=3840:2160:flags=fast_bilinear[fx_alpha]")
        filter_chains.append(f"[{current_stream}][fx_alpha]overlay=x=0:y=0:format=auto[m_fx]")
        current_stream = "m_fx"

    if sub_path and sub_path.is_file():
        clean_sub = sub_path.resolve().as_posix().replace(":", r"\\:")
        clean_font = f":fontsdir={Path(fonts_dir).resolve().as_posix().replace(':', r'\\:')}" if fonts_dir and Path(fonts_dir).is_dir() else ""
        filter_chains.append(f"[{current_stream}]subtitles=filename={clean_sub}{clean_font}[v_out]")
    else:
        filter_chains.append(f"[{current_stream}]null[v_out]")

    audio_idx = count
    a_f = "loudnorm=I=-14.0:TP=-1.0:LRA=7.0" if enable_loudnorm else "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
    filter_chains.append(f"[{audio_idx}:a]{a_f}[a_out]")
    return extra_args, ";".join(filter_chains)
