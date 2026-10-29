"""Documentary Pass 2 Directorial Motion & Audio-First Shot Cadence Service.

Directs shot-level duration allocation and camera movement choreography
(local drone sequential/parallel arrays, Ken Burns, and AI video diffusion)
by querying Gemini as the sole creative Director with real measured chapter audio durations.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.providers.base import HTTPClientPool
from src.studios.documentary_studio.doc_shot_flattening import _normalize_coords, flatten_chapters_to_scenes


def build_pass2_directorial_prompt(
    screenplay_data: Dict[str, Any],
    chapter_durations: Dict[int, float],
    execution_mode: str = "prod",
) -> str:
    """Build the Pass 2 directorial prompt layered on Base Directorial Prompt & Documentary Screenplay Blueprint."""
    from src.core.prompt_routing_service import get_prompt_blueprint
    from src.studios.base_directorial_prompt import build_base_directorial_prompt

    title = screenplay_data.get("title", "Documentary")
    dest = screenplay_data.get("destination_entity") or title.split(":")[0].strip()
    genre = screenplay_data.get("genre") or "doc/nations"
    sub_genre = screenplay_data.get("sub_genre") or "europe_nations"
    archetype = screenplay_data.get("primary_archetype") or "country_overview"
    chapters = screenplay_data.get("chapters") or screenplay_data.get("scenes") or []
    is_prod = str(execution_mode).lower() == "prod"
    diff_model = "kling_v3_4k" if is_prod else "h3_max"
    total_speech = sum(chapter_durations.values()) if chapter_durations else 120.0

    base_prompt = build_base_directorial_prompt(
        genre=genre, sub_genre=sub_genre, archetype=archetype, cluster="documentary",
        custom_prompt=f"{dest}: {title}", duration_seconds=total_speech,
        num_shots=len(chapters) * 3, camera_motion="perspective_drone",
        channel_id=screenplay_data.get("channel_id") or "euro_discovery",
        tier="balanced", execution_mode=execution_mode,
    )
    doc_blueprint = get_prompt_blueprint("documentary", genre, sub_genre, archetype, stage="screenplay")

    ch_summary = []
    for idx, ch in enumerate(chapters, 1):
        ch_idx = ch.get("chapter_index") or idx
        real_dur = chapter_durations.get(ch_idx) or float(ch.get("duration_seconds") or 12.0)
        ch_title = ch.get("chapter_title") or f"Chapter {ch_idx}"
        coords = _normalize_coords(ch.get("origin_coords"))
        narr = (ch.get("narration_text") or ch.get("narration") or "")[:140]
        loc_hub = ch.get("location_hub") or ch_title
        vd = ch.get("visual_directive") if isinstance(ch.get("visual_directive"), dict) else {}
        vd_hint = f" | Directives: {vd.get('establishing_shot', '')[:70]}" if vd else ""
        ch_summary.append(
            f"Chapter {ch_idx}: '{ch_title}' (Coords: {coords})\n"
            f"  Location Hub: {loc_hub}{vd_hint}\n"
            f"  Measured Narration Duration: {real_dur:.2f} seconds\n"
            f"  Narrative Context: {narr}..."
        )
    chapters_context = "\n\n".join(ch_summary)

    return f"""{base_prompt}

=== DOCUMENTARY SCREENPLAY BLUEPRINT ===
{doc_blueprint}

=== PASS 2 AUDIO-FIRST 3-ANGLE SHOT SIZING & LOCAL DRONE CHOREOGRAPHY FOR "{title}" ===
1. VISUAL PADDING & CONTEMPLATION TIME:
   Each chapter's voiceover has been recorded ("Measured Narration Duration"). Add "visual_padding_seconds" (2.0s to 6.0s) so "chapter_total_duration" = Measured Narration Duration + visual_padding_seconds.
2. MULTI-ANGLE SHOT PROGRESSION & STRICT 5.0s AI DIFFUSION CAP:
   Author 3 or more distinct shots in each chapter's "shots" array (you may create 3, 4, or 5 shots per chapter as needed) whose "duration_seconds" sum EXACTLY to "chapter_total_duration":
   - Shot 1 (High Aerial Vista): 18mm ultra-wide panoramic high-altitude bird's-eye perspective ("local_drone", $0.00).
   - Shot 2 (45° Top View / 3D Orbit): 45-degree angle top view or 3D orbital banking flight around the landmark ("local_drone", $0.00).
   - Shot 3+ (Living Kinetic Perspective & Complementary Local Drone Angles):
     * STRICT 5.0s AI DIFFUSION CONSTRAINT: For cost saving, EVERY shot with "motion_type": "ai_diffusion" ("{diff_model}") MUST be assigned "duration_seconds": 5.0 (STRICTLY 5.0s, never longer!).
     * Use complementary "local_drone" ($0.00) shots (and add a 4th or 5th shot if helpful) to cover the remaining duration of the chapter so all shots in the chapter sum EXACTLY to "chapter_total_duration"!
3. LOCAL PERSPECTIVE DRONE ("motion_type": "ken_burns", "recommended_model": "local_drone") NATIVE SCHEMA:
   - In "model_configs.local_drone", use ONLY native engine primitives:
     "dollyin", "dollyout", "slow-drone-forward", "slow-drone-pullback", "crane-ascend", "crane-descent", "drone-sweep-left", "drone-sweep-right", "pan-left", "pan-right", "tilt-up", "tilt-down", "orbit-left", "orbit-right", "drift-up-right", "drift-up-left", "drift-down-right", "drift-down-left", "roll-left", "roll-right", "level", "stay".
   - Parallel stage format: {{"stage": 1, "duration": 10.0, "movements": ["slow-drone-forward", "tilt-down"]}}
   - Sequential stage format: {{"stage": 2, "duration": 10.0, "movement": "crane-ascend"}}
   - Include "camera_movement": "<primary_primitive>", "start_pan": "center"|"left"|"right", "start_zoom": "normal"|"in", "start_tilt": "center"|"up"|"down", "curve": "cosine"|"cubic"|"ramp-up"|"ramp-down".
4. GEMINI AUTONOMOUS MOTION DECISION ("local_drone" vs "{diff_model}"):
   - YOU (Gemini) autonomously decide for every single shot whether it should use "local_drone" or "{diff_model}" based strictly on what is inside the shot (no fixed quota):
   - Choose "motion_type": "ken_burns", "recommended_model": "local_drone" ($0.00) when the shot depicts purely static subjects (stone monuments, historic interiors, libraries, manuscripts, ruins, statues, or solid terrain without moving objects).
   - Choose "motion_type": "ai_diffusion", "recommended_model": "{diff_model}" whenever the shot contains any movable or dynamic objects—including humans, pedestrians, crowds, artisans, vehicles (cars, buses, trucks, trains), boats, ships, birds, airplanes, water (rivers, canals, ocean waves, lakes, waterfalls), clouds, skies, smoke, or fire—so those elements animate naturally and never look frozen! Populate "motion_prompt" and "model_configs.{diff_model}".
   - MANDATORY 5.0-SECOND CAP ON AI DIFFUSION: Every "{diff_model}" shot MUST have `"duration_seconds": 5.0`! Allocate the remaining seconds of `"chapter_total_duration"` across the complementary `"local_drone"` shots (adding additional `"local_drone"` shots if needed) so the chapter's shots sum EXACTLY to `"chapter_total_duration"`.

=== CHAPTERS & REAL MEASURED AUDIO DURATIONS ===
{chapters_context}

=== RESPONSE FORMAT ===
Output strictly minified, valid JSON with root "title", "total_duration_seconds", and "chapters" array. Each chapter contains "chapter_index", "chapter_title", "origin_coords", "visual_padding_seconds", "chapter_total_duration", and "shots" array.
"""


def _fallback_pass2_allocation(
    screenplay_data: Dict[str, Any],
    chapter_durations: Dict[int, float],
    execution_mode: str = "prod",
) -> Dict[str, Any]:
    """Deterministic fallback synthesizing 3-angle multi-shot coverage per chapter with visual padding."""
    updated = dict(screenplay_data)
    chapters = updated.get("chapters") or updated.get("scenes") or []
    out_chapters: List[Dict[str, Any]] = []
    tot_dur = 0.0

    for idx, ch in enumerate(chapters, 1):
        ch_idx = ch.get("chapter_index") or idx
        speech_dur = round(chapter_durations.get(ch_idx) or float(ch.get("duration_seconds") or 12.0), 2)
        vis_pad = float(ch.get("visual_padding_seconds") or 3.0)
        tot_ch_dur = round(speech_dur + vis_pad, 2)
        tot_dur += tot_ch_dur

        coords = _normalize_coords(ch.get("origin_coords"))
        ch_title = ch.get("chapter_title") or f"Chapter {ch_idx}"
        loc_hub = ch.get("location_hub") or ch_title
        vd = ch.get("visual_directive") if isinstance(ch.get("visual_directive"), dict) else {}

        ch_copy = dict(ch)
        ch_copy["chapter_index"] = ch_idx
        ch_copy["chapter_title"] = ch_title
        ch_copy["narration_text"] = ch.get("narration_text") or ch.get("narration") or ""
        ch_copy["chapter_audio_duration"] = speech_dur
        ch_copy["visual_padding_seconds"] = vis_pad
        ch_copy["chapter_total_duration"] = tot_ch_dur
        ch_copy["origin_coords"] = coords

        is_living = "action" in loc_hub.lower() or "market" in loc_hub.lower()
        if is_living and tot_ch_dur > 12.0:
            d3 = 5.0
            rem = round(tot_ch_dur - d3, 2)
            d1 = round(rem * 0.5, 2)
            d2 = round(rem - d1, 2)
        else:
            d1 = round(tot_ch_dur * 0.35, 2)
            d2 = round(tot_ch_dur * 0.35, 2)
            d3 = round(tot_ch_dur - d1 - d2, 2)

        vp1 = vd.get("establishing_shot") or f"Hyper-realistic 4K UHD aerial drone vista of {loc_hub}, 18mm lens, vibrant natural colors."
        vp2 = vd.get("kinetic_shot") or f"Dramatic 4K 45-degree angled bird's-eye top view flight circling {loc_hub}, Hasselblad clarity."
        vp3 = vd.get("detail_shot") or f"Close-up tactile architectural relief and environmental detail of {loc_hub}, 85mm optical bokeh."

        shot1 = {
            "shot_index": 1, "shot_type": "wide_aerial_panoramic", "location_hub": f"{loc_hub} Vista",
            "origin_coords": coords, "duration_seconds": d1, "motion_type": "ken_burns", "recommended_model": "local_drone",
            "camera_movement": "dollyin", "visual_prompt": vp1,
            "model_configs": {"local_drone": {"model": "local_perspective_drone", "movements": [{"duration": round(d1 * 0.5, 2), "motion": "dollyin"}, {"duration": round(d1 * 0.5, 2), "motion": "level"}], "curve": "cosine"}},
        }
        shot2 = {
            "shot_index": 2, "shot_type": "top_view_orbital", "location_hub": f"{loc_hub} Top View",
            "origin_coords": coords, "duration_seconds": d2, "motion_type": "ken_burns", "recommended_model": "local_drone",
            "camera_movement": "orbit-right", "visual_prompt": vp2,
            "model_configs": {"local_drone": {"model": "local_perspective_drone", "movements": [{"duration": round(d2 * 0.6, 2), "motion": "orbit-right"}, {"duration": round(d2 * 0.4, 2), "motion": "dollyout"}], "curve": "cosine"}},
        }
        is_living = "action" in loc_hub.lower() or "market" in loc_hub.lower()
        shot3 = {
            "shot_index": 3, "shot_type": "ground_tactile_detail", "location_hub": f"{loc_hub} Detail",
            "origin_coords": coords, "duration_seconds": d3,
            "motion_type": "ai_diffusion" if is_living else "ken_burns",
            "recommended_model": ("kling_v3_4k" if execution_mode == "prod" else "h3_max") if is_living else "local_drone",
            "camera_movement": "slow_drone_forward", "visual_prompt": vp3,
            "model_configs": {"local_drone": {"model": "local_perspective_drone", "movements": [{"duration": d3, "motion": "slow_drone_forward"}], "curve": "cosine"}},
        }
        ch_copy["shots"] = [shot1, shot2, shot3]
        out_chapters.append(ch_copy)

    updated["chapters"] = out_chapters
    updated["total_duration_seconds"] = round(tot_dur, 2)
    return updated


async def execute_pass2_directorial_motion(
    screenplay_data: Dict[str, Any],
    chapter_durations: Dict[int, float],
    raw_output_path: Optional[os.PathLike | str] = None,
    execution_mode: str = "prod",
    allow_fallback: bool = True,
) -> Dict[str, Any]:
    """Execute Pass 2 directorial query with Gemini, persisting the finalized directorial screenplay."""
    from datetime import datetime, timezone
    from src.providers.base import is_mock_mode
    from src.providers.llm.gemini_adapter import get_live_gemini_api_key

    all_chapters = screenplay_data.get("chapters") or screenplay_data.get("scenes") or []
    prompt = build_pass2_directorial_prompt(screenplay_data, chapter_durations, execution_mode)

    def _persist_outputs(result_payload: Dict[str, Any], model_used: str) -> None:
        if not raw_output_path:
            return
        p = Path(raw_output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        sp_inputs = {
            "model": model_used,
            "execution_mode": execution_mode,
            "title": screenplay_data.get("title", "Documentary"),
            "destination_entity": screenplay_data.get("destination_entity", ""),
            "total_chapters": len(all_chapters),
            "chapter_durations": chapter_durations,
            "system_prompt": prompt,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        (p.parent / "gemini_screenplay_inputs.json").write_text(json.dumps(sp_inputs, indent=2, ensure_ascii=False), encoding="utf-8")

    if is_mock_mode():
        logger.info("pass2_directorial_motion: Running deterministic mock (test environment)")
        base_res = _fallback_pass2_allocation(screenplay_data, chapter_durations, execution_mode)
        _persist_outputs(base_res, "offline_deterministic_mock")
        return base_res

    api_key = get_live_gemini_api_key()
    if not api_key:
        if allow_fallback:
            base_res = _fallback_pass2_allocation(screenplay_data, chapter_durations, execution_mode)
            _persist_outputs(base_res, "offline_fallback")
            return base_res
        raise RuntimeError("Pass 2 Directorial Motion halted: Google Gemini API key is missing or not configured in environment.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4, "maxOutputTokens": 65536},
    }
    client = HTTPClientPool.get_client()
    parsed: Dict[str, Any]
    try:
        resp = await client.post(url, json=payload, timeout=120.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error (HTTP {resp.status_code}): {resp.text[:300]}")
        data = resp.json()
        cands = data.get("candidates", [])
        if not cands:
            raise RuntimeError(f"Gemini returned zero candidates: {data}")
        raw_text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        if raw_text.startswith("```"):
            raw_text = "\n".join(ln for ln in raw_text.splitlines() if not ln.startswith("```")).strip()
        parsed = json.loads(raw_text)
    except Exception as ex:
        logger.warning(f"pass2_directorial_motion_fallback_triggered: {ex}")
        if not allow_fallback:
            raise RuntimeError(f"Pass 2 Directorial Motion failed: {ex}") from ex
        parsed = _fallback_pass2_allocation(screenplay_data, chapter_durations, execution_mode)

    _persist_outputs(parsed, "gemini-flash-latest")
    logger.info(f"pass2_directorial_motion_succeeded: {len(parsed.get('chapters', []))} chapters directed")
    return parsed


_DRONE_ACTION_MAP = {
    "push_in": "dollyin", "push-in": "dollyin", "zoom_in": "dollyin",
    "pull_back": "dollyout", "pull-back": "dollyout", "zoom_out": "dollyout",
    "slow_drone_forward": "slow-drone-forward", "drone_forward": "slow-drone-forward",
    "slow_drone_pullback": "slow-drone-pullback", "drone_pullback": "slow-drone-pullback",
    "crane_ascend": "crane-ascend", "crane_descent": "crane-descent",
    "drone_sweep_left": "drone-sweep-left", "drone_sweep_right": "drone-sweep-right",
}


def _map_drone_act(act: Any) -> str:
    s = str(act or "dollyin").strip().lower()
    return _DRONE_ACTION_MAP.get(s, s.replace("_", "-"))


def translate_doc_drone_configs(m_cfgs: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
    """Translate screenplay model_configs.local_drone into the exact schema local_perspective_drone.py expects."""
    out_cfgs = dict(m_cfgs) if isinstance(m_cfgs, dict) else {}
    ld = dict(out_cfgs.get("local_drone") or {})
    cam_mov = _map_drone_act(ld.get("camera_movement") or "dollyin")
    raw_movs = ld.get("movements")
    if isinstance(raw_movs, list) and raw_movs:
        norm_movs = []
        for step in raw_movs:
            if not isinstance(step, dict):
                continue
            dur = float(step.get("duration") or step.get("duration_seconds") or 5.0)
            par = step.get("parallel") or (step.get("movements") if isinstance(step.get("movements"), list) else None)
            if isinstance(par, list) and par:
                norm_movs.append({"duration": dur, "movements": [_map_drone_act(x) for x in par]})
            else:
                single = step.get("motion") or step.get("movement") or step.get("action") or cam_mov
                norm_movs.append({"duration": dur, "movement": _map_drone_act(single)})
        if norm_movs:
            ld["movements"] = norm_movs
    ld["camera_movement"] = cam_mov
    out_cfgs["local_drone"] = ld
    return out_cfgs, cam_mov


__all__ = [
    "build_pass2_directorial_prompt",
    "_fallback_pass2_allocation",
    "flatten_chapters_to_scenes",
    "execute_pass2_directorial_motion",
    "translate_doc_drone_configs",
]
