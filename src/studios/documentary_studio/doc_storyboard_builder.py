"""Helper builder for constructing typed DocScene instances from raw screenplay scenes."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.studios.documentary_studio.doc_templates import DocScene
from src.studios.directorial_configs import build_default_image_model_configs
from src.services.motion_tier_router import scene_has_humans


def build_doc_scene_list(
    raw_scenes: List[Dict[str, Any]],
    dur_per_scene: float,
    is_geo_mode: bool,
    dest_entity: Optional[str],
    tour_mode: bool,
    domain_tag: str,
    default_model: str,
) -> List[DocScene]:
    """Constructs validated, typed DocScene instances with correct motion and camera framing."""
    doc_scenes: List[DocScene] = []
    total_scenes = len(raw_scenes)

    for idx, sc in enumerate(raw_scenes):
        sc_dur = max(2.0, float(sc.get("duration_seconds", dur_per_scene)))
        v_prompt = sc.get("visual_prompt") or sc.get("visual_description", "")
        loc_hub = sc.get("location_hub") or sc.get("scene_title") or sc.get("landmark_name") or sc.get("title") or "Scenic Vista"
        cam_rig = sc.get("camera_rig") or ("locked_tripod_telephoto" if "locked_tripod" in str(sc.get("shot_type", "")) else "heavy_lift_cine_drone")
        cam_move = sc.get("camera_movement") or ("locked_stationary_cinemagraph" if cam_rig == "locked_tripod_telephoto" else "slow_drone_forward")
        m_prompt = sc.get("motion_prompt") or sc.get("camera_movement_description") or f"Cinematic 4K capture from {cam_rig}. {cam_move} overlooking landscape. Natural environmental micro-motion."
        mot_type = sc.get("motion_type") or "ken_burns"
        mot_rationale = sc.get("motion_rationale") or f"Tier-0 4K drone cinematography via {cam_move} ($0.00 compute)."
        n_text = sc.get("narration_text") or sc.get("narration") or sc.get("audio_narration") or sc.get("voiceover") or ""

        if is_geo_mode and idx == 0:
            sc_dur = max(10.0, min(12.0, sc_dur if sc_dur >= 9.0 else 11.0))
            mot_type = "ken_burns"
            sc["recommended_model"] = "local_drone"
            if not cam_move or cam_move == "locked_stationary_cinemagraph":
                cam_move = "slow_drone_forward"
            if dest_entity and not any(k in n_text.lower() for k in ("welcome to", "in the heart", "paradox", "enigma", "lies a sovereign", "across the")):
                n_text = f"Welcome to {dest_entity}. {n_text}".strip()
        elif is_geo_mode and idx == total_scenes - 1 and total_scenes >= 2:
            sc_dur = max(10.0, min(12.0, sc_dur if sc_dur >= 9.0 else 11.0))
            mot_type = "ken_burns"
            sc["recommended_model"] = "local_drone"
            cam_move = "dollyout"
            if not n_text:
                n_text = f"From its ancient foundations to its vibrant living spirit, {dest_entity or 'this remarkable destination'} stands as an enduring testament to culture, beauty, and wonder."

        shot_type_val = str(sc.get("shot_type", "")).lower()
        is_tour_overview = bool(sc.get("is_itinerary_overview", False) or (tour_mode and (idx == 0 and "overview" in shot_type_val)))
        is_tour_summary = bool(sc.get("is_itinerary_summary", False) or (tour_mode and (idx == total_scenes - 1 and "summary" in shot_type_val)))
        is_tour_vacation = bool(sc.get("is_vacation_scope", False) or (tour_mode and "vacation" in shot_type_val))
        is_map_trans = bool(sc.get("is_map_transition", False) or (tour_mode and any(k in shot_type_val for k in ("map", "transition", "cartographic"))))
        is_info_slide = is_map_trans or is_tour_overview or is_tour_vacation or is_tour_summary
        if is_info_slide:
            cam_rig, cam_move, mot_type = "locked_tripod_telephoto", "locked_stationary_cinemagraph", "ken_burns"
            m_prompt, mot_rationale = "Static locked tripod hold on 4K display.", "Static infographic hold ($0.00 compute)."

        attr_name = None if is_tour_overview else (sc.get("attraction_name") or sc.get("origin_name"))
        if not is_info_slide and not any(k in v_prompt.lower() for k in ("panoramic", "ultra-wide", "wide vista", "establishing shot")):
            v_prompt = f"{v_prompt}, expansive panoramic landscape vista, 18mm ultra-wide architectural lens, generous sky headroom and foreground breathing room"

        ld_cfg = (sc.get("model_configs") or {}).get("local_drone") or {}
        drone_choreo = ld_cfg.get("movement") or sc.get("camera_movement") or sc.get("drone_choreography")
        start_framing = sc.get("start_framing") or {"pan": ld_cfg.get("start_pan", "center"), "zoom": ld_cfg.get("start_zoom", "normal"), "tilt": ld_cfg.get("start_tilt", "center")}
        motion_curve = ld_cfg.get("curve") or sc.get("motion_curve", "cosine")
        if isinstance(drone_choreo, str) and not is_info_slide:
            cam_move = drone_choreo

        sc_rec = str(sc.get("recommended_model") or sc.get("motion_model") or "").strip().lower()
        has_hum = scene_has_humans(f"{v_prompt} {m_prompt}")
        if is_geo_mode and idx == 0:
            rec_model = "local_drone"
        elif sc.get("motion_type") in ("ai_diffusion", "diffusion", "neural"):
            rec_model = "kling_v3_4k" if (has_hum or "kling" in sc_rec) else (sc_rec if sc_rec and sc_rec not in ("auto", "local_drone") else "h3_max")
        else:
            rec_model = sc_rec or default_model

        img_cfgs = sc.get("image_model_configs") or (build_default_image_model_configs(v_prompt, loc_hub or "Scene") if v_prompt else {})

        doc_scenes.append(
            DocScene(
                scene_index=idx + 1,
                duration_seconds=sc_dur,
                shot_type=sc.get("shot_type", "wide" if idx == 0 else "medium"),
                motion_domain=sc.get("domain") or domain_tag,
                recommended_model=rec_model,
                visual_prompt=v_prompt,
                motion_prompt=m_prompt,
                narration_text=n_text,
                motion_engine=sc.get("motion_engine", "local_drone"),
                drone_choreography=drone_choreo,
                start_framing=start_framing,
                motion_curve=motion_curve,
                weather=sc.get("weather", "none"),
                is_map_transition=is_map_trans,
                attraction_name=attr_name,
                origin_name=sc.get("origin_name") or sc.get("scene_title"),
                destination_name=sc.get("destination_name"),
                origin_coords=sc.get("origin_coords"), destination_coords=sc.get("destination_coords"),
                distance_local=sc.get("distance_local"), transit_mode=sc.get("transit_mode", "walk"),
                day_number=int(sc.get("day_number", 1) or 1),
                start_time=sc.get("start_time"), end_time=sc.get("end_time"),
                visit_duration=sc.get("visit_duration"), transit_duration=sc.get("transit_duration"),
                attraction_cost=sc.get("attraction_cost"), is_itinerary_overview=is_tour_overview,
                is_itinerary_summary=is_tour_summary, is_vacation_scope=is_tour_vacation,
                camera_rig=cam_rig, camera_movement=cam_move, motion_type=mot_type, motion_rationale=mot_rationale,
                location_hub=loc_hub, color_temp_kelvin=int(sc.get("color_temp_kelvin") or 5500),
                chapter_index=sc.get("chapter_index"), is_chapter_head=bool(sc.get("is_chapter_head", True)),
                model_configs=sc.get("model_configs"),
                image_model_configs=img_cfgs,
                motion_negative_prompt=sc.get("motion_negative_prompt") or "tight crop, cropped building, cut off steeple, claustrophobic framing, camera shake, jitter, artifacts",
            )
        )

    return doc_scenes


__all__ = ["build_doc_scene_list"]
