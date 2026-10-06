"""Base Directorial Prompt Builder for CineAI Studio Agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.config.channel_registry import get_channel_profile
from src.studios.lighting_director import detect_lighting_directive, format_universal_lighting_guardrails


def build_default_image_model_configs(prompt: str, landmark_name: str = "Landmark") -> Dict[str, Any]:
    """Universal multi-model image configurations for FLUX Dev, FLUX Pro Ultra, and Z-Image Turbo."""
    clean_p = prompt.strip()
    return {
        "flux_dev": {
          "model": "fal-ai/flux/dev",
          "prompt": f"A photorealistic, symmetrical 16:9 cinematic landscape view of {landmark_name}. Shot on locked tripod. {clean_p}. Pristine natural wilderness, zero buildings, zero tourists, zero vehicles.",
          "aspect_ratio": "16:9",
          "guidance_scale": 3.5,
          "num_inference_steps": 28,
        },
        "flux_pro": {
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": f"Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. Symmetrical 16:9 cinematic framing, shot on a locked tripod. {clean_p}. Pristine untouched wilderness, strictly zero humans, zero modern structures, zero vehicles.",
          "aspect_ratio": "16:9",
          "raw": True,
        },
        "zimage": {
          "model": "fal-ai/z-image/turbo",
          "prompt": f"Stunning photorealistic panoramic landscape of {landmark_name}, 16:9 locked tripod framing, {clean_p}, pristine nature, 8k, sharp focus.",
          "aspect_ratio": "16:9",
          "num_inference_steps": 8,
        },
    }


def build_default_video_model_configs(fluid_motion: str, static_elements: str = "Rock cliffs and landscape structure") -> Dict[str, Any]:
    """Universal multi-model video diffusion directives for Wan 2.1 and Kling Pro."""
    return {
        "wan_2_1": {
            "model": "fal-ai/wan-i2v",
            "prompts": {
                "positive_prompt": f"Living wallpaper cinemagraph, completely stationary static frame. {static_elements} remain 100% frozen and unmoving. {fluid_motion}, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible.",
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, parched, frozen ice, stagnant water, artifacts, humans, tourist, boat, railings, buildings",
            },
            "settings": {
                "guide_scale": 5.0,
                "num_inference_steps": 30,
                "aspect_ratio": "16:9",
            },
        },
        "kling_v1_6_pro": {
            "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
            "prompts": {
                "positive_prompt": f"Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. {static_elements} remain 100% frozen and static. {fluid_motion}, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans.",
                "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water",
            },
            "settings": {
                "mode": "pro",
                "duration": "5",
                "aspect_ratio": "16:9",
            },
        },
    }


def build_base_directorial_prompt(
    genre: str,
    sub_genre: str,
    archetype: str,
    cluster: str,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 6.0,
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
    eff_shots = num_shots if num_shots > 0 else max(1, round(duration_seconds / 20.0))
    per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
    target_words = max(25, int(duration_seconds * 1.95))
    per_shot_words = max(12, int(target_words / max(1, eff_shots)))
    clean_tier = (tier or "balanced").strip().lower()
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

    is_urban_or_travel = genre.startswith("travel") or archetype in ("cities", "tourist_places", "iconic_places", "spiritual_places")
    if is_urban_or_travel:
        d1 = """1. 4K CINEMATIC DRONE ARCHITECTURAL & SCENIC SHOWCASE:
   - For Cities & Skylines: Show magnificent architectural skylines, gleaming glass towers reflecting sky, suspension bridges, and historic monuments from a sweeping 4K aerial drone perspective in crisp natural daytime (evening/night lights ONLY if user explicitly requested night).
   - For Heritage & Citadels: Show monumental ancient architecture, grand stone ramparts, temples, and palaces.
   - Zero Tourist Crowd Clutter: Keep focus on breathtaking architectural monuments, skylines, and landscape geometry."""
    else:
        d1 = """1. PURE PRISTINE UNINHABITED NATURE (ZERO HUMANS, ZERO STRUCTURES):
   - Every scene MUST be 100% uninhabited, wild, raw, primordial nature.
   - Absolutely zero humans, tourists, swimmers, hikers, guides, voices, or faces.
   - Strictly zero modern structures, buildings, cabins, paved roads, vehicles, fences, power lines, boats, or railings."""

    return f"""You are the Master Visual Director and Senior Cinematic Storyboard Artist for CineAI Studio.
Your role is to author a complete, production-ready, broadcast-grade Screenplay for the "{genre}" channel genre.

{channel_block}
{lighting_block}

======================================================================
UNIVERSAL CINEMATIC DIRECTIVES (MANDATORY FOR ALL SCENES):
======================================================================
{d1}

2. LIVING WALLPAPER & BALANCED CINEMATIC COMPOSITION:
   - Format visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH.
   - In "shot_type", use "wide_panoramic_picturesque".
   - In "visual_prompt", format for high-stability 16:9 landscape framing on a locked tripod with balanced natural depth.
   - In "motion_prompt", ALWAYS anchor with: "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming."

3. HYBRID MOTION DIRECTORIAL SCRIPT CONTRACT (TIER: {clean_tier.upper()}):
   - SCRIPT IS THE MANDATORY FOUNDATION FOR PRODUCTION. Every scene MUST explicitly specify "motion_type" ("ai_diffusion" | "ken_burns") and "motion_rationale". Zero fallbacks allowed; downstream execution halts if missing.
   - Cinematic Tier: Set "motion_type": "ai_diffusion" for 100% of scenes.
   - Low-Cost Tier: Set "motion_type": "ken_burns" for 100% of scenes.
   - Balanced Tier (Directorial Kinetic Allocation):
     * MANDATORY "ai_diffusion": living subjects (people, performers, animals, birds), fluid dynamics (rivers, waves, falls, rain, embers, steam), macro kinetics (swaying flower petals, rustling leaves), or moving vehicles.
     * MANDATORY "ken_burns": rigid monumental terrain (distant mountain peaks, granite cliffs, dunes) and architecture (stone temples, palaces, room walls) to preserve 100% geometry at $0.00 compute.
   - Anti-Motion-Fatigue Clear Sky Standard: Skies MUST be crystal-clear, cloudless azure skies. STRICTLY PROHIBIT drifting clouds.
   - Multi-Waypoint Kinetic Choreography: In "camera_waypoints", provide an array of sub-movements and durations summing to duration_seconds (e.g. slow_drone_forward, pan_right, crane_up, reveal_pull_back) so the camera moves smoothly without repetitive loops.
   - Wide-Scale Micro-Kinetics: In "kinetic_micro_zones", specify optional normalized bboxes [ymin, ymax, xmin, xmax] (0.0-1.0) for "sprites" (cars, people, boats drifting via delta_pct), "tree_sway_zones", and "water_zones".
   - Domain Specification: Set "water_fluid" for water/rain/falls, "landscape_solid" for mountain/citadels/forest, or "cozy_hearth" for fires.

4. MULTI-MODEL IMAGE PROMPTS ("image_model_configs"):
   - For every scene, author model-tailored landscape prompts for "flux_dev" (natural balanced), "flux_pro" (8K Hasselblad raw), and "zimage" (punchy 8-step turbo).

5. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs"):
   - For every scene, author model-tailored positive/negative prompts for "kling_v1_6_pro" (directorial action) and "wan_2_1" (continuous fluid kinetic).

6. MANDATORY NEGATIVE PROMPT:
   - For Pure Wilderness: Always include: "clouds, cloudy, overcast sky, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings".
   - For Cozy Living / Bedrooms / Cabins / Walking Tours: Prohibit structural drift, flickering, and artifacts, but DO NOT ban architectural structures: "clouds, cloudy, overcast sky, cumulus, storm clouds, moving clouds, timelapse, camera movement, camera pan, panning, tilt, zoom, morphing architecture, changing furniture, structural drift, flickering, temporal jump, changing lighting, gelatinous water, melting foam, rubbery water, static vertical streaks, falling wire artifacts, artifacts, humans, tourist, clutter, plastic junk, modern electronics".

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
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Camera Rig: {camera_motion}
- Target Image Models: ["flux_dev", "flux_pro", "zimage"]
- Target Video Models: ["kling_v1_6_pro", "wan_2_1"]

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:
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
    "suno_musical_tags": "432Hz meditative soundbath, joyful uplifting handpan, singing bowls, warm velvet synth pads, deep stress relief, peaceful sleep drone, zero solo guitar, -21 LUFS",
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
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": {eff_kelvin},
      "visual_prompt": "A photorealistic, symmetrical 16:9 cinematic landscape view of [Landmark Name], shot on locked tripod. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles.",
      "image_model_configs": {{
        "flux_dev": {{"model": "fal-ai/flux/dev", "prompt": "Photorealistic wide panoramic view of [Landmark Name], 16:9 cinematic.", "aspect_ratio": "16:9", "guidance_scale": 3.5, "num_inference_steps": 28}},
        "flux_pro": {{"model": "fal-ai/flux-pro/v1.1-ultra", "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c of [Landmark Name], 16:9.", "aspect_ratio": "16:9", "raw": true}},
        "zimage": {{"model": "fal-ai/z-image/turbo", "prompt": "Stunning photorealistic panoramic landscape of [Landmark Name], 16:9, sharp focus.", "aspect_ratio": "16:9", "num_inference_steps": 8}}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement.",
      "motion_negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, artifacts",
      "model_configs": {{
        "wan_2_1": {{"model": "fal-ai/wan-i2v", "prompts": {{"positive_prompt": "Living wallpaper cinemagraph, fluid motion.", "negative_prompt": "camera movement, artifacts"}}, "settings": {{"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"}}}},
        "kling_v1_6_pro": {{"model": "fal-ai/kling-video/v1.6/pro/image-to-video", "prompts": {{"positive_prompt": "Cinemagraph living wallpaper.", "negative_prompt": "camera movement, artifacts"}}, "settings": {{"mode": "pro", "duration": "5", "aspect_ratio": "16:9"}}}}
      }},
      "domain": "water_fluid",
      "motion_type": "ai_diffusion",
      "camera_movement": "slow_zoom_in",
      "camera_waypoints": [
        {{"motion": "slow_drone_forward", "duration_seconds": 15.0}},
        {{"motion": "pan_right", "duration_seconds": 15.0}},
        {{"motion": "crane_up", "duration_seconds": 10.0}}
      ],
      "kinetic_micro_zones": {{
        "sprites": [{{"label": "car_eastbound", "bbox": [0.72, 0.74, 0.30, 0.33], "delta_pct": [0.08, 0.0]}}],
        "tree_sway_zones": [[0.20, 0.50, 0.80, 0.95]],
        "water_zones": [[0.65, 0.95, 0.10, 0.90]]
      }},
      "motion_rationale": "Fluid water surface requires live AI diffusion for natural ripples",
      "duration_seconds": {per_shot_dur},
      "narration_text": "Evocative, continuous narration for this vista (~{per_shot_words} words) paced smoothly for {per_shot_dur}s."
    }}
  ],
  "publishing": {{
    "ctr_titles": [
      "3 HOURS of Deep Serenity in [Landmark] ⋄ 432Hz Healing Soundbath to Calm Your Mind - 4K UHD",
      "Sleep Under [Landmark Sky/Nature] ✦ 432Hz Miracle Tone for Instant Anxiety Relief & Rest - 4K",
      "[Landmark] Living Wallpaper ⋄ 4K 60FPS Ambient Living Room & Soothing Resonance"
    ],
    "description_with_timestamps": "Immerse yourself in the majestic beauty of [Landmark Name]. Filmed with broadcast 4K clarity, authentic spatial acoustics, and tranquil soundscapes.\\n\\n⏱️ Chapters:\\n0:00 - Sanctuary Vista\\n\\n🌿 Sanctuary Details:\\n- Location: [Landmark Name], [Country]\\n- Audio: 432Hz Natural Spatial Soundscape\\n- Mastered for deep sleep, meditation, and focus.",
    "seo_tags": ["nature relaxation", "living wallpaper", "4k nature", "meditation soundscape", "sleep aid", "ambient nature"],
    "has_synthetic_media": true,
    "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)",
    "thumbnail_concept_prompts": [
      "Ultra-crisp 16:9 cinematic shot of [Landmark Name], striking lighting, vibrant natural colors, award-winning landscape photography."
    ]
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""
