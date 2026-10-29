"""Broadcast Single-Pass Filtergraph Builder with 4K Dossier Overlay Support.

Constructs optimal FFmpeg filtergraphs combining:
1. 4K UHD adaptive resolution scaling and 24fps standardization
2. Timed educational lower-third dossier cards (Option A: 1.0s fade-in, hold to 5.5s, 0.5s fade-out)
3. Broadcast xfade transitions between sequential scene clips
4. Audio sidechain ducking and broadcast master fade-outs
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.core.telemetry import logger
from src.services.ambient_export_service import build_adaptive_resolution_filter, get_media_duration


def ensure_dossier_overlay_cards(
    ep_dir: Optional[Path],
    position: str = "bottom_left",
) -> Dict[int, Path]:
    """Ensures 4K transparent PNG overlay cards exist for documentary chapter heads."""
    if not ep_dir or not ep_dir.is_dir():
        return {}

    raw_p = ep_dir / "raw_gemini_screenplay.json"
    sp_p = ep_dir / "screenplay.json"
    source = raw_p if (raw_p.is_file() and raw_p.stat().st_size > 100) else (sp_p if sp_p.is_file() else None)
    if not source:
        return {}

    cards: Dict[int, Path] = {}
    try:
        from PIL import Image
        from src.studios.documentary_studio.doc_dossier_card_service import save_dossier_card_png

        data = json.loads(source.read_text("utf-8"))
        g_all = f"{data.get('genre', '')} {data.get('sub_genre', '')} {data.get('primary_archetype', '')} {str(ep_dir).lower()}".lower()
        is_edu_doc = any(k in g_all for k in ("doc", "tour", "nation", "places", "cities", "countries", "country"))
        scenes = data.get("scenes", [])
        if not scenes and data.get("chapters"):
            from src.studios.documentary_studio.doc_chapter_cadence_service import flatten_chapters_to_timeline_shots
            scenes, _ = flatten_chapters_to_timeline_shots(data)
        if not is_edu_doc and not any(sc.get("chapter_title") or sc.get("fact_badge") for sc in scenes):
            return {}
        for idx, sc in enumerate(scenes):
            if sc.get("is_chapter_head") is False:
                continue
            card_p = ep_dir / f"overlay_p{idx + 1}.png"
            needs_render = not card_p.is_file() or card_p.stat().st_size < 1000
            if not needs_render and card_p.is_file():
                try:
                    with Image.open(card_p) as c_img:
                        bb = c_img.getbbox()
                        if bb:
                            is_tr = bb[0] > 1920 and bb[1] < 1080
                            if position == "top_right" and not is_tr:
                                needs_render = True
                            elif position == "bottom_left" and is_tr:
                                needs_render = True
                except Exception:
                    needs_render = True

            if needs_render:
                title = sc.get("chapter_title")
                badge = sc.get("fact_badge")
                sub = sc.get("chapter_subtitle")
                stats = sc.get("chapter_stats")
                if title or badge:
                    save_dossier_card_png(
                        output_path=card_p,
                        chapter_title=title or f"CHAPTER {idx + 1}",
                        chapter_subtitle=sub,
                        stats=stats,
                        badge=badge,
                        position=position,
                    )
            if card_p.is_file() and card_p.stat().st_size > 1000:
                cards[idx] = card_p
    except Exception as ex:
        logger.debug(f"ensure_dossier_cards_error: {ex}")

    return cards


def build_broadcast_filtergraph(
    seamless_clips: List[Path],
    hold_list: List[float],
    x_dur: float,
    audio_path: Optional[Path],
    no_loop: bool = False,
    ep_dir: Optional[Path] = None,
) -> Tuple[List[str], str, str, Optional[str], float]:
    """Builds single-pass inputs, filter_complex string, video tag, audio tag, and target duration."""
    n = len(seamless_clips)
    inputs: List[str] = []

    # 1. Video Clip Inputs
    for i, c in enumerate(seamless_clips):
        c_dur = get_media_duration(c) or 5.0
        c_hold = hold_list[i] if i < len(hold_list) else c_dur
        if c_dur < c_hold - 0.5:
            v_loops = max(1, int(c_hold / max(1.0, c_dur)) + 2)
            inputs.extend(["-stream_loop", str(v_loops)])
        inputs.extend(["-i", str(c)])

    # 2. Lower-Third Educational Cards Inputs
    resolved_dir = ep_dir or (seamless_clips[0].parent if seamless_clips else None)
    card_map_paths = ensure_dossier_overlay_cards(resolved_dir)
    card_stream_idx: Dict[int, int] = {}
    curr_input_idx = n

    for i in range(n):
        card_file = card_map_paths.get(i) or (resolved_dir / f"overlay_p{i + 1}.png" if resolved_dir else None)
        if card_file and card_file.is_file() and card_file.stat().st_size > 1000:
            inputs.extend(["-loop", "1", "-t", "8", "-i", str(card_file)])
            card_stream_idx[i] = curr_input_idx
            curr_input_idx += 1

    # 3. Audio Input
    audio_stream_idx = None
    if audio_path and audio_path.is_file():
        audio_stream_idx = f"{curr_input_idx}:a"
        inputs.extend(["-i", str(audio_path)])

    # 4. Construct Filtergraph Chains
    filter_parts: List[str] = []
    for i, c in enumerate(seamless_clips):
        res_filter = build_adaptive_resolution_filter(c, 3840, 2160)
        c_dur = hold_list[i] if i < len(hold_list) else (get_media_duration(c) or 5.0)

        if i in card_stream_idx:
            k = card_stream_idx[i]
            c_fade_out = max(2.5, min(5.5, c_dur - 1.0))
            filter_parts.append(f"[{i}:v]{res_filter},fps=24[base{i}]")
            filter_parts.append(
                f"[{k}:v]format=rgba,fade=t=in:st=1.0:d=0.5:alpha=1,fade=t=out:st={c_fade_out:.2f}:d=0.5:alpha=1[c_fade{i}]"
            )
            filter_parts.append(f"[base{i}][c_fade{i}]overlay=0:0[s{i}]")
        else:
            filter_parts.append(f"[{i}:v]{res_filter},fps=24[s{i}]")

    # 5. Connect Scene Clips with XFade Transitions
    prev_tag, curr_offset = "s0", max(0.1, hold_list[0] - x_dur)
    for i in range(1, n):
        out_tag = f"v{i}" if i < n - 1 else "v"
        filter_parts.append(
            f"[{prev_tag}][s{i}]xfade=transition=fade:duration={x_dur:.2f}:offset={max(0.1, curr_offset):.2f}[{out_tag}]"
        )
        prev_tag = out_tag
        curr_offset += max(0.1, (hold_list[i] - x_dur) if i < n - 1 else hold_list[i])

    target_dur = round(curr_offset, 2)
    return inputs, ";".join(filter_parts), "v", audio_stream_idx, target_dur


__all__ = ["build_broadcast_filtergraph", "ensure_dossier_overlay_cards"]
