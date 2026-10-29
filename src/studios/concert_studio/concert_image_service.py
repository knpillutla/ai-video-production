"""4K Concert Camera Rig Image Synthesis Service.
Produces Plate 1 master at stage eye level with dynamic outfits and model prompts.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
from src.providers.visual.fal_aura_sr import FalAuraSRAdapter
from src.providers.visual.fal_flux_dev import FalFluxDevAdapter
from src.providers.visual.fal_flux_lora import FalFluxLoraAdapter
from src.providers.visual.fal_flux_pro_ultra import FalFluxProUltraAdapter
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.providers.visual.fal_zimage_lora import FalZImageLoraAdapter
from src.services.image_color_harmonizer import harmonize_image_colors
from src.studios.concert_studio.concert_setting_catalog import resolve_concert_setting
from src.studios.concert_studio.concert_prompt_engine import detect_chorus_presence

CONCERT_CAMERA_NAMES = ["singer_orchestra_stage"]


def _build_lead_character_prompt(storyboard_data: dict[str, Any], raw_prompt: str, trigger_words: str, instrument: str = "mic") -> str:
    """Build character-locked prompt for Plate 1 (Singer + Orchestra) at stage eye level."""
    chars = storyboard_data.get("characters") or []
    c = chars[0] if chars else {}
    name = c.get("name", "Singer")
    v_gen = str(storyboard_data.get("vocal_gender") or c.get("gender") or "").lower()
    is_male = "male" in v_gen and "fe" not in v_gen
    eff_inst = (instrument or storyboard_data.get("instrument") or "mic").lower()
    has_custom = eff_inst not in ("mic", "none", "vocal", "vocals")
    inst_name = eff_inst.replace("_", " ").title()
    is_dj = bool(storyboard_data.get("is_dj") or "dj" in str(storyboard_data.get("style", "")).lower())
    title_role = f"DJ {name}" if is_dj else (f"lead singer and {inst_name} virtuoso {name}" if has_custom else f"lead singer {name}")
    wardrobe = storyboard_data.get("character_wardrobe") or {}
    default_outfit = "handsome tailored concert jacket with structured collar and tailored trousers" if is_male else "elegant sapphire blue and gold silk anarkali gown with high jewel neckline, fully covered chest and torso, long fitted sleeves"
    default_acc = "precision chronograph wristwatch strapped securely to left wrist" if is_male else "delicate gold necklace choker and matching earrings"
    if is_dj:
        default_acc = "professional over-ear DJ headphones around neck, precision chronograph watch strapped securely to left wrist"
    outfit = wardrobe.get("outfit_description") or default_outfit
    acc = wardrobe.get("accessories") or default_acc
    pronoun = "He" if is_male else "She"
    physique = "handsome, lean-athletic fit build" if is_male else "24 years old, fit slender build"
    pos = str(storyboard_data.get("artist_position") or storyboard_data.get("position") or "").lower()
    is_sitting = "sit" in pos
    style = str(storyboard_data.get("style", "")).lower()
    has_chorus = detect_chorus_presence(storyboard_data)
    c_sit = ", and 2-3 backing chorus vocalists seated gracefully at microphones harmonizing" if has_chorus else ""
    c_stand = ", and 2-3 backing chorus vocalists standing at choir microphones swaying in rhythm and harmonizing" if has_chorus else ""

    if is_dj:
        posture_action = "standing centerstage behind an illuminated DJ booth console with multi-channel CDJ mixer and jog wheels, cueing tracks and hyping crowd"
        flank_ensemble = "Surrounding the DJ booth are towering LED visual walls, laser arrays, and subwoofer stacks"
    elif has_custom:
        if "carnatic" in style or "classical" in style or "hindustani" in style or is_sitting:
            posture_action = f"seated cross-legged centerstage on ornate Persian carpet holding and playing {inst_name} as virtuoso; microphone positioned strictly below chin level at upper chest, mouth and lips fully visible and unobstructed"
            flank_ensemble = f"Flanked side-by-side on the same carpeted stage dais by the live acoustic rhythm ensemble: mridangam percussionist seated on stage right playing mridangam drum, and ghatam percussion artist on stage left{c_sit}"
        else:
            posture_action = f"standing centerstage playing {inst_name} passionately as virtuoso; microphone positioned strictly below chin level at upper chest with open space between chin and microphone, lips and mouth completely unobstructed"
            flank_ensemble = f"Flanked on the wooden stage deck at eye level by the live concert rhythm section: bassist on stage left and drummer on drum kit on stage right{c_stand}"
    elif "carnatic" in style or "classical" in style or "hindustani" in style or is_sitting:
        posture_action = "seated cross-legged centerstage on ornate Persian carpet with classical hand mudras; holding wireless microphone gracefully in hand lowered strictly below chin at upper chest level, clear open space between chin and microphone, entire face, mouth, lips, and teeth 100% visible and unobstructed (zero microphone covering mouth, singing only, not playing instruments)"
        flank_ensemble = f"Flanked side-by-side on the same carpeted stage dais by the live acoustic orchestra: acoustic violinist seated on stage left playing violin, and mridangam percussionist seated on stage right playing mridangam drum{c_sit}"
    else:
        posture_action = "standing centerstage with dynamic stage presence; holding wireless microphone in hand lowered strictly below chin at upper chest level with wide visible separation between chin and microphone, entire face, mouth, lips, and teeth 100% visible and unobstructed (zero microphone covering mouth, singing only, not playing instruments)"
        flank_ensemble = f"Flanking on the wooden stage deck at eye level is the live concert orchestra: electric guitarist on stage left and drummer on drum kit on stage right{c_stand}"

    v_preset = resolve_concert_setting(
        storyboard_data.get("setting"), venue_type=storyboard_data.get("venue_type"),
        time_of_day=storyboard_data.get("time_of_day"), stage_setting=storyboard_data.get("stage_setting"),
        background=storyboard_data.get("background"), weather=storyboard_data.get("weather"),
    )
    stage_env = f"Authentic {v_preset.stage_environment} at {v_preset.display_name} directly overlooking {v_preset.background.replace('_', ' ')}."
    lighting_env = f"{v_preset.lighting_environment} ({v_preset.time_of_day}), pristine optical clarity, zero artificial yellow haze"
    ctx = f" {raw_prompt.strip()}." if raw_prompt and len(raw_prompt.strip()) > 30 else ""
    return (
        f"Hyper-realistic 4K UHD concert stage master shot shot on Hasselblad H6D-100c prime lens of {title_role}, {trigger_words}, {physique}, "
        f"{posture_action}. {pronoun} wears an attractive, stylish, and elegant {outfit}, "
        f"adorned with {acc}. Dignified non-exposing attire (zero cleavage, covered chest, covered midriff, covered waist and torso). "
        f"{flank_ensemble}. {stage_env} {lighting_env}.{ctx} "
        f"Wide-angle eye-level framing, vibrant saturated colors, warm golden amber lighting, razor-sharp micro-textures, 8k resolution."
    )


def _build_cutaway_prompt(
    raw_prompt: str, camera_name: str, instrument: str = "acoustic_guitar", storyboard_data: dict[str, Any] | None = None
) -> str:
    """Build unified environment concert element prompt matching Plate 1 set manifest."""
    clean, wardrobe = raw_prompt.strip(), (storyboard_data or {}).get("character_wardrobe", {})
    outfit = wardrobe.get("outfit_description", "")
    sb = storyboard_data or {}
    style = str(sb.get("style", "")).lower()
    setting = f"{sb.get('setting', '')} {sb.get('background', '')}".lower()
    is_classical = any(k in style for k in ("carnatic", "hindustani", "classical", "fusion"))
    is_beach = any(k in setting for k in ("beach", "ocean", "coastal"))

    if camera_name == "overall_stage_vista":
        anchor = f" Performer in distance visible on stage in identical {outfit}." if outfit else ""
        if clean and len(clean) > 25:
            return f"{clean},{anchor} matching exact stage platform and lighting, eye-level wide perspective, 8k resolution"
        if is_beach:
            return f"Monumental wide architectural open-air seaside stage panorama overlooking rolling ocean waves.{anchor} Identical wooden stage platform, warm ambient lanterns, twilight ocean horizon, eye-level wide perspective, 8k resolution."
        return f"Monumental architectural concert panorama of same physical stage platform.{anchor} Identical stage carpet, lighting temperature, venue backdrop, eye-level wide perspective, 8k resolution."

    if camera_name == "stadium_audience_crowd":
        if clean and len(clean) > 25:
            return f"{clean}, eye-level horizontal perspective, 8k resolution, cinema-grade broadcast concert cinematography"
        if is_classical and is_beach:
            return "Eye-level perspective looking out across serene open-air listeners seated comfortably along seaside promenade, listening in deep appreciation with gentle head nods under warm ambient lanterns, ocean waves in background, zero lightsticks, 8k resolution."
        if is_classical:
            return "Eye-level perspective looking out across serene concert hall audience seated in deep musical appreciation with graceful mudras, warm acoustic hall chandeliers, zero lightsticks, 8k resolution."
        return "Eye-level perspective looking across enthusiastic concert audience cheering towards brilliant stage, eye level horizontal framing, 8k resolution."
    return "Monumental eye-level concert panorama of illuminated central stage deck at night, 8k resolution."


async def validate_concert_modesty(image_path: Path) -> bool:
    """Automated Gemini Flash Vision gate: mic below chin + zero exposed skin."""
    try:
        import base64, json, httpx
        from src.providers.llm.gemini_adapter import get_live_gemini_api_key
        key = get_live_gemini_api_key()
        if not key or not image_path.is_file(): return True
        b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={key}"
        prompt_txt = "Inspect concert singer image: (1) Is the microphone covering, touching, or in front of the mouth or lips? (MUST be held strictly below chin at chest level so mouth/lips are 100% visible for lip-sync). (2) Is there any exposed skin at midriff/waist/chest? Reply strictly JSON: {\"is_compliant\": bool, \"reason\": str}"
        body = {"contents": [{"parts": [{"text": prompt_txt}, {"inline_data": {"mime_type": "image/jpeg", "data": b64}}]}]}
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=body)
            if resp.status_code == 200:
                txt = resp.json()["candidates"][0]["content"]["parts"][0]["text"].replace("```json", "").replace("```", "").strip()
                res = json.loads(txt)
                if not res.get("is_compliant", True):
                    logger.warning(f"visual_gate_rejected: {res.get('reason')}")
                    return False
                return True
    except Exception as ex:
        logger.warning(f"modesty_validation_skipped: {ex}")
    return True


def _resolve_spatial_3d_engine(spatial_3d_engine: str | None, motion_model: str | None) -> str:
    s = (spatial_3d_engine or "").lower()
    m = (motion_model or "").lower()
    if any(k in s for k in ("kling", "king")):
        return "kling"
    if any(k in s for k in ("h3", "minimax")):
        return "h3_max"
    if any(k in m for k in ("kling", "king")):
        return "kling"
    return "h3_max"


async def synthesize_concert_camera_rig(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    user_id: str,
    network: str = "telugu_rhythms",
    force_live: bool = False,
    episode_id: Any = None,
    chars: str = "Radha",
    instrument: str = "mic",
    model: str = "z-image",
    lora_model: str = "z-image",
    dataset_model: str = "z-image",
    motion_model: str = "drone",
    spatial_3d_engine: str | None = None,
    lora_scale: float = 0.82,
) -> list[Path]:
    """Synthesize master concert camera plates (3 plates via Spatial 3D by default, or 2 via legacy)."""
    scenes_dir.mkdir(parents=True, exist_ok=True)
    from src.compositor.vocal_lora_resolver import resolve_vocal_loras
    loras, trigger_words = await resolve_vocal_loras(
        storyboard_data=storyboard_data, char_names=[chars], chars=chars,
        explicit_loras=None, user_id=user_id, network=network, use_loras=True,
        force_live=force_live, lora_model=lora_model, dataset_model=dataset_model,
    )

    scenes_list = storyboard_data.get("scenes") or []
    seed_hash = int(hashlib.sha256(str(episode_id or scenes_dir.parent.name).encode()).hexdigest()[:8], 16)
    song_seed = seed_hash % 900000

    aura_upscaler, flux_lora, z_lora = FalAuraSRAdapter(), FalFluxLoraAdapter(), FalZImageLoraAdapter()
    flux_dev, flux_ultra, z_adapter = FalFluxDevAdapter(), FalFluxProUltraAdapter(), FalZImageAdapter()
    eff_img_model = (model or "z-image").lower()
    resolved: list[Path] = []

    for idx in range(1, len(CONCERT_CAMERA_NAMES) + 1):
        scene_path = scenes_dir / f"scene_{idx:02d}.jpg"
        cam_name = CONCERT_CAMERA_NAMES[idx - 1]
        sc = scenes_list[idx - 1] if idx <= len(scenes_list) else {}
        img_prompts = sc.get("image_prompts", {})

        # Select prompt and negative prompt from Gemini's model-specific output
        if "ultra" in eff_img_model: m_dict = img_prompts.get("flux_pro_ultra", {})
        elif "z" in eff_img_model or "zimage" in eff_img_model: m_dict = img_prompts.get("z_image", {})
        else: m_dict = img_prompts.get("flux_dev", {})

        raw_p = m_dict.get("prompt") or sc.get("visual_prompt", "")
        neg_p = m_dict.get("negative_prompt") or sc.get("negative_prompt", "")

        if idx == 1:
            v_p = resolve_concert_setting(
                storyboard_data.get("setting"), venue_type=storyboard_data.get("venue_type"),
                time_of_day=storyboard_data.get("time_of_day"), stage_setting=storyboard_data.get("stage_setting"),
                background=storyboard_data.get("background"), weather=storyboard_data.get("weather"),
            )
            is_out = v_p.venue_type == "outdoor" or any(k in f"{v_p.stage_setting} {v_p.background}".lower() for k in ("beach", "ocean", "outdoor", "garden", "mountain", "desert", "roof"))
            out_ban = ", indoor, indoor stadium, arena trusses, steel rafters, ceiling, enclosed walls, dark room, concrete stadium bowl" if is_out else ""
            eff_inst = (instrument or storyboard_data.get("instrument") or "mic").lower()
            has_custom = eff_inst not in ("mic", "none", "vocal", "vocals")
            prompt = _build_lead_character_prompt(storyboard_data, raw_p, trigger_words, instrument=instrument)
            neg_b = neg_p or "bare midriff, exposed stomach, bare chest, cleavage, low cut, exposed collarbone, bare shoulders"
            mic_neg = "microphone covering mouth, microphone blocking lips, mic covering face, microphone in front of lips, hand covering mouth, obstructed lips"
            has_chorus = detect_chorus_presence(storyboard_data)
            c_neg = ", missing chorus, missing backing vocalists" if has_chorus else ""
            if has_custom:
                neg_prompt = f"{neg_b}, {mic_neg}{c_neg}{out_ban}, solo portrait, single person, missing {eff_inst}, empty hands, missing orchestra, missing band, empty carpet, tight crop, close-up"
            else:
                neg_prompt = f"{neg_b}, {mic_neg}{c_neg}{out_ban}, solo portrait, single person, singer playing violin, singer holding instrument, missing orchestra, missing band, empty carpet, tight crop, close-up"
        else:
            prompt = _build_cutaway_prompt(raw_p, cam_name, instrument, storyboard_data)
            neg_prompt = neg_p or "cleavage, bare skin, female solo portrait, plastic, blur, flat lighting"

        # Rule 3 Tier 1: Check existing non-empty artifact
        if scene_path.is_file() and scene_path.stat().st_size > 1000:
            if idx == 1 and force_live and not await validate_concert_modesty(scene_path):
                logger.warning(f"cached_plate_failed_gate: removing flawed {scene_path.name} to regenerate")
                scene_path.unlink(missing_ok=True)
            else:
                logger.info(f"concert_camera_{idx:02d}_reused [{cam_name}]: {scene_path.name} ($0.00 spend)")
                await aura_upscaler.upscale_image(scene_path, scene_path, target_res=(3840, 2160), force_live=force_live)
                use_spatial_3d = not (motion_model and any(k in motion_model.lower() for k in ("2-plate", "legacy", "static")))
                if idx == 1 and use_spatial_3d:
                    from src.studios.concert_studio.concert_kling_3d import synthesize_spatial_3d_flight_plates
                    orbit_p, eng = storyboard_data.get("camera_orbit_prompt"), _resolve_spatial_3d_engine(spatial_3d_engine, motion_model)
                    return await synthesize_spatial_3d_flight_plates(scene_path, scenes_dir, force_live, episode_id, custom_orbit_prompt=orbit_p, engine=eng, storyboard_data=storyboard_data)
                continue

        seed = (song_seed + idx * 79) % 900000
        logger.info(f"synthesizing_concert_camera_{idx:02d} [{cam_name}] [model={eff_img_model}]: prompt={prompt[:75]}... (seed={seed})")

        if idx == 1 and loras:
            p_lora = loras[0]["path"]
            import os
            env_s = os.getenv("LORA_SCALE")
            scale = float(env_s) if env_s else float(loras[0].get("scale", lora_scale))
            is_z_lora = "z" in (lora_model or eff_img_model).lower()
            for attempt in range(2):
                cur_p = prompt if attempt == 0 else f"{prompt}, holding microphone lowered strictly below chin at chest level, mouth and lips 100% open and visible with zero microphone in front of face, covered midriff"
                if is_z_lora:
                    await z_lora.generate_with_lora(
                        prompt=cur_p, lora_url=p_lora, output_path=scene_path,
                        lora_scale=scale, aspect_ratio="16:9", seed=seed + attempt * 23, upscale_4k=False,
                        force_live=force_live,
                    )
                else:
                    await flux_lora.generate_with_lora(
                        prompt=cur_p, lora_url=p_lora, output_path=scene_path,
                        lora_scale=scale, aspect_ratio="16:9", seed=seed + attempt * 23, upscale_4k=False,
                        negative_prompt=neg_prompt,
                    )
                if not force_live or await validate_concert_modesty(scene_path):
                    break
                logger.warning(f"visual_gate_failed [attempt {attempt+1}]: regenerating with tighter constraints")
        elif "ultra" in eff_img_model:
            await flux_ultra.generate_to_file(prompt=prompt, output_path=scene_path, aspect_ratio="16:9", force_live=force_live, seed=seed, upscale_4k=False)
        else:
            adapter = z_adapter if ("z" in eff_img_model or "zimage" in eff_img_model) else flux_dev
            await adapter.generate_to_file(prompt=prompt, output_path=scene_path, aspect_ratio="16:9", force_live=force_live, seed=seed, upscale_4k=False)

        # Harmonize color palette of cutaways against Plate 1 Master
        if idx > 1 and (scenes_dir / "scene_01.jpg").is_file():
            harmonize_image_colors(scene_path, scenes_dir / "scene_01.jpg")

        # 4K UHD Mastering
        logger.info(f"upscaling_concert_camera_{idx:02d}_to_4k [model=fal-ai/aura-sr]: target=(3840, 2160)")
        await aura_upscaler.upscale_image(scene_path, scene_path, target_res=(3840, 2160), force_live=force_live)

        if episode_id and scene_path.is_file():
            rights_ledger.record_asset(
                episode_id, AssetType.IMAGE, str(scene_path), "Fal.ai", "Flux/AuraSR",
                CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"CONCERT-CAM-{idx}-{episode_id}", True,
            )
        resolved.append(scene_path)
        use_spatial_3d = not (motion_model and any(k in motion_model.lower() for k in ("2-plate", "legacy", "static")))
        if idx == 1 and use_spatial_3d:
            from src.studios.concert_studio.concert_kling_3d import synthesize_spatial_3d_flight_plates
            orbit_p = storyboard_data.get("camera_orbit_prompt")
            eng = _resolve_spatial_3d_engine(spatial_3d_engine, motion_model)
            return await synthesize_spatial_3d_flight_plates(scene_path, scenes_dir, force_live, episode_id, custom_orbit_prompt=orbit_p, engine=eng, storyboard_data=storyboard_data)

    return resolved

__all__ = ["CONCERT_CAMERA_NAMES", "synthesize_concert_camera_rig"]
