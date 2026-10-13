"""Base Directorial Prompt Builder for CineAI Studio Agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.config.network_registry import get_channel_profile
from src.studios.directorial_configs import (
    build_default_image_model_configs,
    build_default_video_model_configs,
)
from src.studios.lighting_director import detect_lighting_directive, format_universal_lighting_guardrails

# Re-export configuration builders for backwards compatibility
__all__ = [
    "build_default_image_model_configs",
    "build_default_video_model_configs",
    "build_base_directorial_prompt",
]


def build_base_directorial_prompt(
    genre: str, sub_genre: str, archetype: str, cluster: str,
    custom_prompt: Optional[str] = None, duration_seconds: float = 60.0,
    num_shots: int = 1, camera_motion: str = "locked_tripod",
    excluded_topics: Optional[List[str]] = None, specific_rules: str = "",
    curation_landmarks: Optional[List[str]] = None, color_temp_kelvin: int = 5500,
    channel_id: Optional[str] = None, tier: str = "balanced",
    extra_root_schema: str = "", extra_scene_schema: str = "",
    speech_cadence_wpm: int = 120, speech_words_per_sec: float = 2.0,
    tts_provider_name: str = "Azure Speech Neural",
) -> str:
    """Compose the authoritative directorial system prompt for Gemini storyboarding."""
    g_lower, a_lower = (genre or "").lower(), (archetype or "").lower()
    ch_lower, clean_tier = (channel_id or "").lower(), (tier or "balanced").strip().lower()

    is_nature_relax = (
        g_lower.startswith("relax") or "nature" in g_lower
        or a_lower in ("zen", "mountain", "forest", "ocean", "valley", "waterfall", "healing", "rain", "cozy", "blizzard", "hearth", "beach_lounge", "desert")
    )
    is_urban_or_travel = (
        g_lower.startswith("travel") or "travel" in g_lower
        or a_lower in ("cities", "tourist_places", "iconic_places", "spiritual_places", "natural_wonders", "remote_places")
        or ch_lower == "skylinediariesindia4k" or (ch_lower == "earth_serenade" and not is_nature_relax) or num_shots == -1
    )
    is_documentary = "doc" in g_lower or "documentary" in ch_lower or "doc" in (sub_genre or "").lower() or "documentary" in a_lower

    tour_archetypes = {
        "itinerary_map_tour", "travel_itinerary_tour", "grand_tour", "top_attractions_tour",
        "local_neighborhood_tour", "culinary_food_tour", "architecture_design_tour",
    }
    is_tour = (a_lower in tour_archetypes) or ((sub_genre or "").lower().strip() in tour_archetypes)
    user_chose_fixed_shots = (num_shots is not None and num_shots > 0 and num_shots != -1)
    if user_chose_fixed_shots:
        eff_shots = num_shots
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = f"- Target Duration: ~{duration_seconds}s (Directorial buffer enabled) | Explicit Shots: {eff_shots} (~{per_shot_dur}s/shot)"
        schema_mandate = f"\n- Generate exactly {eff_shots} scene(s) matching the requested shot count inside 'scenes' with duration matching narration."
    elif is_tour:
        eff_shots = max(5, round(duration_seconds / 9.0))
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = (
            f"- Target Duration: ~{duration_seconds}s (Directorial buffer enabled) | Autonomous Tour Cadence:\n"
            f"  * Autonomously determine the exact number of scenes based on the tour duration and planned landmarks.\n"
            f"  * Mandatory structure: Scene 1: Overview Flowchart Card, followed by each Attraction and its connecting Route Map, ending with the Master Recap Table slide."
        )
        schema_mandate = (
            f"\n- Autonomously generate the complete set of scenes inside 'scenes' matching the tour route and duration. "
            f"Every planned landmark MUST have its own dedicated physical scene, followed by a connecting route map slide, concluding with the Master Recap Table."
        )
    else:
        eff_shots = max(2, round(duration_seconds / 12.0)) if (is_urban_or_travel or duration_seconds > 18.0) else max(1, round(duration_seconds / 6.0))
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = (
            f"- Target Duration: ~{duration_seconds}s (Directorial buffer enabled) | Autonomous Cadence:\n"
            f"  * Curate {eff_shots} scenes (~{per_shot_dur}s each) with durations dynamically matched to narration length."
        )
        schema_mandate = f"\n- Generate {eff_shots} scenes inside 'scenes' with duration dynamically matched to narration."

    target_words = max(25, int(duration_seconds * speech_words_per_sec))
    per_shot_words = max(8, int(per_shot_dur * speech_words_per_sec))
    eff_kelvin, tod_key, tod_desc = detect_lighting_directive(custom_prompt, archetype, color_temp_kelvin or 5500)
    lighting_block = format_universal_lighting_guardrails(tod_key, eff_kelvin, tod_desc)

    exclusion_block = ("\nPREVIOUSLY PRODUCED TOPICS (MANDATORY DEDUPLICATION):\n" + "\n".join(f"- {t}" for t in excluded_topics[-15:]) + "\n") if excluded_topics else ""
    landmarks_list = "\n".join(f"      {idx}. {lm}" for idx, lm in enumerate(curation_landmarks or [], 1)) if curation_landmarks else ""
    landmarks_block = f"\nCURATED REGIONAL LANDMARK INSPIRATION:\n{landmarks_list}\n" if landmarks_list else ""
    channel_block = f"\n{profile.format_directorial_guardrails_block()}\n" if channel_id and (profile := get_channel_profile(channel_id)) else ""

    motion_rule = (
        f"3. HYBRID MOTION DIRECTORIAL CONTRACT (TIER: {clean_tier.upper()}):\n"
        '   - Gemini DECIDES "motion_type" ("ken_burns" | "ai_diffusion") and "motion_rationale" for every scene.\n'
        '   - Default for stable landscapes & geometry: "ken_burns" ($0.00 compute local 4K perspective engine).\n'
        '   - Select "ai_diffusion" only if complex kinematics (waterfalls, running fauna) strictly require neural video.\n'
        '   - SEQUENTIAL & PARALLEL MULTI-STAGE MOVEMENTS: Direct sequential timeline arrays (e.g. [{"movement": "dollyin", "duration": 6.0}, {"movement": "zoomin", "duration": 4.0}]) or parallel compound movements matching scene duration.'
    )

    if is_nature_relax:
        d1 = ("1. PURE PRISTINE UNINHABITED NATURE & LIVING WALLPAPER (ZERO HUMANS, ZERO STRUCTURES):\n"
              "   - Every scene MUST be 100% uninhabited, wild, raw, primordial nature overlooking a majestic scenery.\n"
              "   - Strictly zero humans, tourists, swimmers, hikers, guides, voices, or faces.\n"
              "   - Zero modern structures, buildings, cabins, paved roads, vehicles, fences, power lines, boats, or railings.\n"
              "   - Living Wallpaper Framing: Compose as a tranquil living wallpaper overlooking the scenic expanse.")
        is_low = clean_tier in ("low_cost", "tier_0", "local")
        if is_low:
            ex_motion_type = "ken_burns"
            ex_rationale = "Fixed locked tripod overlooking natural scenery via local 4K steady hold ($0.00 compute)."
            motion_rule = (
                "3. TIER-0 / LOW-COST LOCKED TRIPOD KEN BURNS DIRECTORIAL CONTRACT ($0.00 COMPUTE):\n"
                '   - MANDATORY "motion_type": "ken_burns" for all relaxation scenes.\n'
                '   - STRICT LOCKED TRIPOD MANDATE: Relaxation format strictly mandates a FIXED LOCKED TRIPOD overlooking scenery with 0 panning, tilting, orbiting, or zooming.\n'
                '   - "camera_movement": strictly ["stay"] or locked stationary hold stage.\n'
                '   - "motion_rationale": "Fixed locked tripod overlooking natural scenery via local 4K steady hold ($0.00 compute)."'
            )
        else:
            ex_motion_type = "ai_diffusion"
            ex_rationale = "Living wallpaper cinemagraph via AI video diffusion animating natural water and foliage kinematics."
            motion_rule = (
                f"3. HYBRID AI DIFFUSION LIVING WALLPAPER CONTRACT (TIER: {clean_tier.upper()}):\n"
                '   - MANDATORY "motion_type": "ai_diffusion" for living nature, water, rivers, falls, ocean, foliage, and living wallpapers.\n'
                '   - "camera_movement": strictly "locked_stationary_cinemagraph".\n'
                '   - "camera_rig": strictly "locked_tripod_telephoto".\n'
                '   - "motion_rationale": "Living wallpaper cinemagraph via AI diffusion for natural fluid/foliage kinematics."'
            )
        rig_palette = '["locked_tripod_telephoto"]'
        default_rig = "locked_tripod_telephoto"
        default_cam_move = "locked_stationary_cinemagraph"
        cam_contract = (
            "4. FIXED LOCKED TRIPOD OVERLOOKING SCENERY (RELAXATION MANDATE):\n"
            "   - Relaxation format (across all genres, archetypes, and weathers) strictly mandates a FIXED LOCKED TRIPOD overlooking scenery.\n"
            "   - 'camera_rig': strictly 'locked_tripod_telephoto' overlooking the natural vista.\n"
            "   - 'camera_movement': strictly 'locked_stationary_cinemagraph' (or ['stay']) with 0 panning, tilting, or zooming.\n"
            "   - Motion: Direct ONLY organic environmental micro-motion (water ripples, swaying leaves, drifting mist/snow).\n"
            "   - Individual genres/archetypes/weather add their own unique atmospheric & sensory properties on top."
        )
    else:
        d1 = ("1. 4K CINEMATIC BLUE-CHIP DOCUMENTARY & DRONE SHOWCASE:\n"
              "   - Dynamic Scenic Cadence: Curate distinct world-class natural landmarks, architecture, and habitats.\n"
              "   - NO MOVING OBJECTS DIRECTIVE: Still, timeless landscape keyframes with ZERO moving objects.\n"
              "   - Authoritative Measured Narration: Measured, poetic, educational voiceover (~120 WPM).\n"
              "   - 100% Crisp Natural Lighting: Balanced daylight or dramatic authentic golden/blue hour.")
        ex_motion_type = "ken_burns"
        ex_rationale = "100% local 4K perspective drone flight via ken_burns compound choreography ($0.00 compute)."
        rig_palette = '["heavy_lift_cine_drone", "technocrane_jib", "stabilized_steadicam_gimbal", "motorized_cine_slider"]'
        default_rig = "heavy_lift_cine_drone"
        default_cam_move = "stay" if is_nature_relax else "dollyin"
        cam_contract = (
            "4. CAMERA RIG & MOTION DIRECTORIAL CONTRACT:\n"
            "   - For AI diffusion models (kling, wan), camera motion is directed in natural language in their prompts.\n"
            "   - For local drone ('model_configs.local_drone'), motion MUST use supported engine movements: 'stay', 'dollyin', 'dollyout', 'pan-left', 'pan-right', 'tilt-up', 'tilt-down', 'drift-up-right', 'drift-up-left', 'drift-down-right', 'drift-down-left', 'orbit-left', 'orbit-right', or stage arrays.\n"
            "   - Root 'camera_movement' MUST mirror the primary movement string ('stay', 'dollyin', 'pan-right', etc.)."
        )

    root_ext = f"{extra_root_schema.strip()}\n" if extra_root_schema and extra_root_schema.strip() else ""
    scene_ext = f"{extra_scene_schema.strip()}\n" if extra_scene_schema and extra_scene_schema.strip() else ""

    return f"""You are the Master Visual Director and Senior Cinematic Storyboard Artist for CineAI Studio.
Your role is to author a complete, production-ready, broadcast-grade Screenplay for the "{genre}" channel genre.

{channel_block}
{lighting_block}

======================================================================
UNIVERSAL CINEMATIC DIRECTIVES (MANDATORY FOR ALL SCENES):
======================================================================
{d1}

2. LIVING WALLPAPER & BALANCED CINEMATIC COMPOSITION:
   - Format visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH with wide panoramic grandeur.
   - In "shot_type", use cinematic panoramic classifications: "wide_panoramic_picturesque", "aerial_grandeur_vista", "low_angle_monumental", or "architectural_perspective_50mm".

{motion_rule}

{cam_contract}

5. DIRECTORIAL SCENE CADENCE & DURATION BUFFER (+LEEWAY):
   - Target Total Duration: ~{duration_seconds}s (Directorial Leeway Buffer of +15% to +25%, or up to +60s for tours is explicitly permitted).
   - Allocate duration based on shot grandeur: 4s-6s (detail/establishing), 8s-12s (orbit/lateral glide), 14s-20s (monumental hold / transit maps).
   - DIRECTORIAL RULE: If a scene requires more narrative context or transit explanation, Gemini MUST INCREASE 'duration_seconds' to match: required_duration = (word_count / {speech_words_per_sec:.2f}) + 1.5s pause. Never truncate narration or rush speech!

6. MULTI-MODEL PROMPTS ("image_model_configs" & "model_configs"):
   - For AI models ("kling_v1_6_pro", "wan_2_1"): camera/atmospheric motion is directed in natural language within their prompt text.
   - For "local_drone": camera flight capabilities MUST be specified inside "model_configs.local_drone":
     * Single movement: "movement": "dollyin"|"pan-right"|"orbit-left" (or stage arrays), "start_pan": "center"|"left"|"right", "start_zoom": "normal"|"wide"|"in", "curve": "cosine". For relaxation format, strictly "movement": "stay".

7. MANDATORY NEGATIVE PROMPT:
   - For Pure Wilderness: "clouds, cloudy, overcast sky, moving clouds, timelapse clouds, camera shake, jitter, rapid motion, flickering, temporal jump, parched, frozen ice, stagnant water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings".
   - For Architectural & Travel: "clouds, overcast sky, moving clouds, camera shake, jitter, rapid motion, morphing architecture, changing furniture, structural drift, flickering, temporal jump, gelatinous water, artifacts, humans, tourist, clutter, plastic junk, modern electronics".

8. NARRATION ENGINE & AUDIO-VISUAL GROUNDING CONTRACT (MANDATORY):
   - Active Narration Engine: {tts_provider_name} ({speech_cadence_wpm} WPM, ~{speech_words_per_sec:.2f} words/sec). Tail breathing pause: 1.5s.
   - Per-Scene Word Formula: Max words = (duration_seconds - 1.5s) * {speech_words_per_sec:.2f}. Total script ~{target_words} words.
   - Divide narration smoothly across 'scenes[].narration_text' perfectly matching each shot's 'duration_seconds'.
   - MANDATORY AUDIO-VISUAL GROUNDING (SHOW-AND-TELL RULE): Every scene's 'narration_text' MUST DIRECTLY DESCRIBE AND INTERPRET WHAT IS VISIBLE ON SCREEN in that scene's 'visual_prompt'. Strictly prohibit phantom subjects (e.g., describing rivers when viewing desert reservoirs, or narrating handheld artifacts in wide drone vistas).
   - Continuous Camera Motion: Visual camera motion runs for the FULL duration of the scene, ensuring continuous flight while narration speaks with ZERO frozen frames.
   - "suno_musical_tags" & "suno_prompt": Autonomously compose bespoke cultural acoustic tags matching geography and mood.

{specific_rules}
{landmarks_block}
{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{custom_prompt or 'Autonomously curate the greatest world-famous natural landmark on Earth'}"
- Genre: {genre}
- Sub-Genre: {sub_genre}
- Primary Archetype: {archetype}
- Geographic Cluster: {cluster}
- Motion & Quality Tier: {clean_tier}
{cadence_spec}
- Camera Rig Palette: {rig_palette}
- Target Image Models: ["flux_dev", "flux_pro", "zimage"]
- Target Video Models: ["kling_v1_6_pro", "wan_2_1", "local_drone"]

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:{schema_mandate}
{{
  "production_id": "EP-001",
  "title": "Authentic Atmospheric Title for the specific location",
  "story_topic": "Detailed sensory synopsis tailored to the true geography",
  "genre": "{genre}",
  "sub_genre": "{sub_genre}",
  "primary_archetype": "{archetype}",
  "secondary_archetype": null,
  "cluster": "{cluster}",
  "tier": "{clean_tier}",
  "primary_language": "en",
  "target_dubbing_languages": ["en", "de", "fr", "ja", "es"],
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
{root_ext}  "global_culture": {{
    "continent_region": "Autonomously derive true continent/region",
    "culture_heritage": "Authentic regional natural and conservation heritage",
    "authentic_textiles_and_fabrics": "Authentic natural materials (weathered stone, moss, river slate, native timber)",
    "cultural_gestures_and_rituals": "Mindful contemplation of nature and tranquil silence"
  }},
  "travel_tourism": {{
    "destination_name": "True Geographic Landmark Name",
    "country": "Authentic Country",
    "province_state": null,
    "attraction_type": "Autonomously derive true topographical structure",
    "best_season_and_lighting": "Autonomously derive optimal season and lighting"
  }},
  "cast": [],
  "audio_master": {{
    "audio_mode": "ambient_nature",
    "spoken_narration_script": "Continuous unbroken master voiceover (~{target_words} words for {duration_seconds}s at 125 WPM), seamlessly narrating the journey without loops.",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "432Hz meditative soundbath, joyful handpan, warm velvet synth pads, deep stress relief, -21 LUFS",
    "vocal_gender": "none", "tempo_bpm": 64, "speech_cadence_wpm": 125, "target_lufs": -14.0, "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Specific Vista 1 Name",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{default_rig}",
      "color_temp_kelvin": {eff_kelvin},
      "visual_prompt": "A photorealistic, symmetrical 16:9 cinematic landscape view of [Landmark Name], shot from {default_rig}. Crisp natural lighting.",
{scene_ext}      "image_model_configs": {{
        "flux_dev": {{"model": "fal-ai/flux/dev", "prompt": "Photorealistic wide panoramic view, 16:9 cinematic.", "aspect_ratio": "16:9", "guidance_scale": 3.5, "num_inference_steps": 28}},
        "flux_pro": {{"model": "fal-ai/flux-pro/v1.1-ultra", "prompt": "Ultra-photorealistic 8K UHD shot, 16:9.", "aspect_ratio": "16:9", "raw": true}}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Smooth panoramic sweep across natural landscape.",
      "motion_negative_prompt": "camera shake, jitter, rapid motion, morphing landscape, artifacts",
      "model_configs": {{
        "wan_2_1": {{"model": "fal-ai/wan-i2v", "prompts": {{"positive_prompt": "Smooth fluid motion.", "negative_prompt": "camera shake, artifacts"}}, "settings": {{"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"}}}},
        "kling_v1_6_pro": {{"model": "fal-ai/kling-video/v1.6/pro/image-to-video", "prompts": {{"positive_prompt": "Cinematic visual grandeur.", "negative_prompt": "camera shake, artifacts"}}, "settings": {{"mode": "pro", "duration": "5", "aspect_ratio": "16:9"}}}},
        "local_drone": {{"model": "local_perspective_drone", "movement": "{'stay' if is_nature_relax else 'dollyin'}", "start_pan": "center", "start_zoom": "normal", "curve": "cosine", "rationale": "{ex_rationale}"}}
      }},
      "domain": "landscape_solid",
      "motion_type": "{ex_motion_type}",
      "camera_movement": "{default_cam_move}",
      "kinetic_micro_zones": {{ "sprites": [], "tree_sway_zones": [], "water_zones": [] }},
      "motion_rationale": "{ex_rationale}",
      "duration_seconds": {per_shot_dur},
      "narration_text": "Evocative, continuous narration for this vista (~{per_shot_words} words) paced smoothly for {per_shot_dur}s."
    }}
  ],
  "publishing": {{
    "ctr_titles": [
      "3 HOURS of Deep Serenity in [Landmark] ⋄ 432Hz Healing Soundbath to Calm Your Mind - 4K UHD",
      "Sleep Under [Landmark Sky/Nature] ✦ 432Hz Miracle Tone for Instant Anxiety Relief & Rest - 4K"
    ],
    "description_with_timestamps": "Immerse yourself in [Landmark Name]. Filmed with broadcast 4K clarity.\\n\\n⏱️ Chapters:\\n0:00 - Sanctuary Vista",
    "seo_tags": ["nature relaxation", "living wallpaper", "4k nature", "ambient nature"],
    "has_synthetic_media": true,
    "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)",
    "thumbnail_concept_prompts": [
      "Ultra-crisp 16:9 cinematic shot of [Landmark Name], striking natural lighting, award-winning photography."
    ]
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""
