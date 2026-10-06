"""Base Directorial Prompt Builder for CineAI Studio Agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.config.channel_registry import get_channel_profile
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
    genre: str,
    sub_genre: str,
    archetype: str,
    cluster: str,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[List[str]] = None,
    specific_rules: str = "",
    curation_landmarks: Optional[List[str]] = None,
    color_temp_kelvin: int = 5500,
    channel_id: Optional[str] = None,
    tier: str = "balanced",
) -> str:
    """Compose the authoritative directorial system prompt for Gemini storyboarding."""
    g_lower = (genre or "").lower()
    a_lower = (archetype or "").lower()
    ch_lower = (channel_id or "").lower()
    clean_tier = (tier or "balanced").strip().lower()

    is_nature_relax = (
        g_lower.startswith("relax")
        or "nature" in g_lower
        or a_lower in (
            "zen", "mountain", "forest", "ocean", "valley", "waterfall",
            "healing", "rain", "cozy", "blizzard", "hearth", "beach_lounge", "desert"
        )
    )

    is_urban_or_travel = (
        g_lower.startswith("travel")
        or "travel" in g_lower
        or a_lower in ("cities", "tourist_places", "iconic_places", "spiritual_places", "natural_wonders", "remote_places")
        or ch_lower == "skylinediariesindia4k"
        or (ch_lower == "earth_serenade" and not is_nature_relax)
        or num_shots == -1
    )

    # User choice for 4K master mode: if user explicitly sets fixed shots for nature relaxing, respect it.
    user_chose_fixed_shots = (num_shots is not None and num_shots > 0 and num_shots != -1)
    if user_chose_fixed_shots and is_nature_relax and clean_tier != "balanced":
        eff_shots = num_shots
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = (
            f"- Total Duration: {duration_seconds} seconds\n"
            f"- Shot Count: {eff_shots} shots ({per_shot_dur}s per shot)\n"
            f"- 4K Master Living Wallpaper Contract: Exactly {eff_shots} scene(s) matching user selection."
        )
        schema_mandate = f"\n- Generate exactly {eff_shots} scenes matching the requested shot count inside 'scenes'."
    else:
        # Balanced mode / autonomous cadence: Dynamic 2s to 12s range across all genres
        eff_shots = max(2, round(duration_seconds / 12.0)) if (is_urban_or_travel or duration_seconds > 18.0) else max(1, round(duration_seconds / 6.0))
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = (
            f"- Total Duration: {duration_seconds} seconds\n"
            f"- Autonomous Cadence Contract (num_shots: -1, Balanced Mode: 2s to 12s Dynamic Range):\n"
            f"  * Dynamic Shot Range: Every scene MUST have duration_seconds between 2.0s and 12.0s (strictly 2.0 <= dur <= 12.0).\n"
            f"  * Cinematic Rhythm: Vary durations across scenes (2s-4s punchy detail/establishing, 5s-8s fluid orbit/reveal, 9s-12s monumental panoramic hold).\n"
            f"  * Mandatory Scene Count: Generate an array of exactly {eff_shots} scenes (~{per_shot_dur}s per shot) summing to {duration_seconds}s.\n"
            f"  * Under NO circumstances generate a monotonous static loop or repeat the same duration for all shots."
        )
        schema_mandate = f"\n- You MUST generate an array of exactly {eff_shots} scenes with dynamic durations (2s-12s) inside 'scenes' for this {duration_seconds}s video."

    target_words = max(25, int(duration_seconds * 1.95))
    per_shot_words = max(12, int(target_words / max(1, eff_shots)))
    eff_kelvin, tod_key, tod_desc = detect_lighting_directive(custom_prompt, archetype, color_temp_kelvin or 5500)
    lighting_block = format_universal_lighting_guardrails(tod_key, eff_kelvin, tod_desc)

    exclusion_block = ""
    if excluded_topics:
        exclusion_block = "\nPREVIOUSLY PRODUCED TOPICS (MANDATORY DEDUPLICATION):\n" + "\n".join(f"- {t}" for t in excluded_topics[-15:]) + "\n"

    landmarks_list = "\n".join(f"      {idx}. {lm}" for idx, lm in enumerate(curation_landmarks or [], 1)) if curation_landmarks else ""
    landmarks_block = f"\nCURATED REGIONAL LANDMARK INSPIRATION:\n{landmarks_list}\n" if landmarks_list else ""

    channel_block = ""
    if channel_id:
        profile = get_channel_profile(channel_id)
        if profile:
            channel_block = "\n" + profile.format_directorial_guardrails_block() + "\n"

    if is_urban_or_travel:
        d1 = """1. 4K CINEMATIC DRONE ARCHITECTURAL & SCENIC SHOWCASE:
   - Dynamic Scenic Cadence (2s-12s per Vista): Curate distinct world-class architectural landmarks across scenes with 2s to 12s dynamic range.
   - For Cities & Skylines: Show magnificent architectural skylines, gleaming glass towers reflecting sky, suspension bridges, and historic monuments from sweeping 4K aerial drone perspectives in crisp natural daytime.
   - For Heritage & Citadels: Show monumental ancient architecture, grand stone ramparts, temples, and palaces.
   - Zero Tourist Crowd Clutter: Keep focus on breathtaking architectural monuments, skylines, and landscape geometry."""
        ex_motion_type = "ken_burns"
        ex_rationale = "100% local 4K perspective drone flight with 2.5D depth parallax and micro-kinetics ($0.00 compute)."
        motion_rule = """3. 100% TIER-0 LOCAL PERSPECTIVE DRONE & MICRO-KINETICS CONTRACT ($0.00 COMPUTE):
   - MANDATORY 100% LOCAL MOTION: Set "motion_type": "ken_burns" for 100% OF SCENES. STRICTLY PROHIBIT "ai_diffusion".
   - Zero AI diffusion calls ($0.00 API expenditure). All 4K motion is handled by the local perspective homography drone engine with multi-waypoint flight choreography ('camera_waypoints') and 2.5D parallax.
   - For all water, trees, and traffic, direct local deterministic kinetics in 'kinetic_micro_zones' (harmonic water ripples via 'water_zones', canopy sway via 'tree_sway_zones', and sprite drifts via 'sprites')."""
    else:
        d1 = """1. PURE PRISTINE UNINHABITED NATURE (ZERO HUMANS, ZERO STRUCTURES):
   - Every scene MUST be 100% uninhabited, wild, raw, primordial nature.
   - Absolutely zero humans, tourists, swimmers, hikers, guides, voices, or faces.
   - Strictly zero modern structures, buildings, cabins, paved roads, vehicles, fences, power lines, boats, or railings."""
        ex_motion_type = "ai_diffusion"
        ex_rationale = "Fluid water surface requires live AI diffusion for natural ripples"
        motion_rule = f"""3. HYBRID MOTION DIRECTORIAL SCRIPT CONTRACT (TIER: {clean_tier.upper()}):
   - SCRIPT IS THE MANDATORY FOUNDATION FOR PRODUCTION. Every scene MUST explicitly specify "motion_type" ("ai_diffusion" | "ken_burns") and "motion_rationale".
   - Balanced Tier: "ai_diffusion" for living subjects & fluid dynamics (rivers, waves, falls, rain, embers, steam); "ken_burns" for rigid monumental terrain (distant peaks, cliffs) to preserve 100% geometry at $0.00 compute.
   - Anti-Motion-Fatigue Clear Sky Standard: Skies MUST be crystal-clear, cloudless azure skies. STRICTLY PROHIBIT drifting clouds.
   - Multi-Waypoint Kinetic Choreography: In "camera_waypoints", provide sub-movements summing to duration_seconds.
   - Wide-Scale Micro-Kinetics: In "kinetic_micro_zones", specify optional normalized bboxes [ymin, ymax, xmin, xmax] (0.0-1.0) for "sprites", "tree_sway_zones", and "water_zones"."""

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

4. CAMERA RIG VS. CAMERA MOVEMENT DIRECTORIAL CONTRACT (MANDATORY):
   - Direct every shot from an authoritative cinematic director's chair with deliberate spatial intention.
   - "camera_rig" defines the PHYSICAL MOUNTING APPARATUS:
     * heavy_lift_cine_drone: Monumental high-altitude aerial sweeps and grand landscape panoramas.
     * technocrane_jib: Smooth vertical elevation reveals, dramatic crane cresting over foreground rocks/trees.
     * cable_cam_system: Fluid, silent glides through canopies, river valleys, or along grand avenues.
     * low_altitude_fpv_rig: Dynamic low-skimming trajectory skimming over water surfaces or open terrain.
     * stabilized_steadicam_gimbal: Smooth eye-level sweeping tracking shots through architectural plazas.
     * locked_tripod_telephoto: Symmetrical, perfectly stable framing for living wallpapers and distant summits.
     * motorized_cine_slider: Silky lateral parallax tracking across foreground textures and foliage.
   - "camera_movement" defines the 3D KINETIC TRAJECTORY:
     * slow_drone_forward: Majestic forward flight into the horizon.
     * dolly_pullback_reveal: Starting close on an architectural or natural motif and expanding backward to reveal scale.
     * orbit_wrap_left / orbit_wrap_right: Sweeping semicircular arc around a focal landmark.
     * tilt_up_monumental_reveal: Starting low and tilting upward to reveal towering heights.
     * crane_pedestal_down / crane_pedestal_up: Vertical elevation glide establishing spatial grandeur.
     * lateral_truck_right / lateral_truck_left: Horizontal tracking across skylines, coastlines, or mountain ranges.
     * low_angle_forward_skim: Skimming low over water or ground level toward the vista.
     * locked_stationary_cinemagraph: 100% frozen frame for pure living wallpaper cinemagraphs.
   - ANTI-MONOTONY GUARD: Consecutive scenes MUST NOT repeat the same camera_rig or camera_movement! Rotate rigs and trajectories to create rich cinematic grandeur.

5. DYNAMIC SHOT DURATION DIRECTIVE (BALANCED MODE: 2s TO 12s RANGE):
   - When in balanced mode, shot durations MUST dynamically vary strictly between 2.0s and 12.0s.
   - Allocate duration based on shot grandeur: 2s-4s (punchy detail/establishing), 5s-8s (orbit/lateral glide), 9s-12s (monumental panoramic hold).
   - The sum of all scene 'duration_seconds' must equal {duration_seconds}s.

6. MULTI-MODEL PROMPTS ("image_model_configs" & "model_configs"):
   - For every scene, author model-tailored landscape prompts for "flux_dev", "flux_pro", and "zimage".
   - Author model-tailored positive/negative prompts for "kling_v1_6_pro" and "wan_2_1".

7. MANDATORY NEGATIVE PROMPT:
   - For Pure Wilderness: "clouds, cloudy, overcast sky, moving clouds, timelapse clouds, camera shake, jitter, rapid motion, flickering, temporal jump, parched, frozen ice, stagnant water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings".
   - For Architectural & Travel: "clouds, overcast sky, moving clouds, camera shake, jitter, rapid motion, morphing architecture, changing furniture, structural drift, flickering, temporal jump, gelatinous water, artifacts, humans, tourist, clutter, plastic junk, modern electronics".

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
- Camera Rig Palette: ["heavy_lift_cine_drone", "technocrane_jib", "cable_cam_system", "stabilized_steadicam_gimbal", "locked_tripod_telephoto", "motorized_cine_slider"]
- Target Image Models: ["flux_dev", "flux_pro", "zimage"]
- Target Video Models: ["kling_v1_6_pro", "wan_2_1"]

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
  "global_culture": {{
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
    "suno_musical_tags": "432Hz meditative soundbath, joyful uplifting handpan, singing bowls, warm velvet synth pads, deep stress relief, peaceful sleep drone, -21 LUFS",
    "vocal_gender": "none",
    "tempo_bpm": 64,
    "speech_cadence_wpm": 125,
    "target_lufs": -14.0,
    "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Specific Vista 1 Name",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "heavy_lift_cine_drone",
      "color_temp_kelvin": {eff_kelvin},
      "visual_prompt": "A photorealistic, symmetrical 16:9 cinematic landscape view of [Landmark Name], shot from heavy lift cine drone. Crisp natural lighting.",
      "image_model_configs": {{
        "flux_dev": {{"model": "fal-ai/flux/dev", "prompt": "Photorealistic wide panoramic view of [Landmark Name], 16:9 cinematic.", "aspect_ratio": "16:9", "guidance_scale": 3.5, "num_inference_steps": 28}},
        "flux_pro": {{"model": "fal-ai/flux-pro/v1.1-ultra", "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c of [Landmark Name], 16:9.", "aspect_ratio": "16:9", "raw": true}},
        "zimage": {{"model": "fal-ai/z-image/turbo", "prompt": "Stunning photorealistic panoramic landscape of [Landmark Name], 16:9, sharp focus.", "aspect_ratio": "16:9", "num_inference_steps": 8}}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Smooth panoramic sweep across natural landscape.",
      "motion_negative_prompt": "camera shake, jitter, rapid motion, morphing landscape, artifacts",
      "model_configs": {{
        "wan_2_1": {{"model": "fal-ai/wan-i2v", "prompts": {{"positive_prompt": "Smooth fluid motion.", "negative_prompt": "camera shake, artifacts"}}, "settings": {{"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"}}}},
        "kling_v1_6_pro": {{"model": "fal-ai/kling-video/v1.6/pro/image-to-video", "prompts": {{"positive_prompt": "Cinematic visual grandeur.", "negative_prompt": "camera shake, artifacts"}}, "settings": {{"mode": "pro", "duration": "5", "aspect_ratio": "16:9"}}}}
      }},
      "domain": "landscape_solid",
      "motion_type": "{ex_motion_type}",
      "camera_movement": "slow_drone_forward",
      "camera_waypoints": [
        {{"motion": "slow_drone_forward", "duration_seconds": 6.0}},
        {{"motion": "orbit_wrap_left", "duration_seconds": 4.0}}
      ],
      "kinetic_micro_zones": {{
        "sprites": [{{"label": "car_eastbound", "bbox": [0.72, 0.74, 0.30, 0.33], "delta_pct": [0.08, 0.0]}}],
        "tree_sway_zones": [[0.20, 0.50, 0.80, 0.95]],
        "water_zones": [[0.65, 0.95, 0.10, 0.90]]
      }},
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
