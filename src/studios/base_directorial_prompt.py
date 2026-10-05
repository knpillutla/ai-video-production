"""Base Directorial Prompt Builder for CineAI Studio Agents.

Authoritative single source of truth for:
- Living Wallpaper & Cinemagraph Rules (Rule 13, Rule 20)
- Multi-Model Image Prompts Contract (FLUX.1-dev, FLUX 1.1 Pro Ultra, Z-Image Turbo)
- Multi-Model Video Diffusion Directives (Wan 2.1, Kling v1.6 Pro / v3)
- Universal RelaxScreenplay Structured JSON Schema
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.config.channel_registry import get_channel_profile


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
) -> str:
    """Compose the authoritative directorial system prompt for Gemini storyboarding."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)

    exclusion_block = ""
    if excluded_topics:
        exclusion_block = "\nPREVIOUSLY PRODUCED TOPICS (MANDATORY DEDUPLICATION):\n" + "\n".join(f"- {t}" for t in excluded_topics[-15:]) + "\n"

    landmarks_list = "\n".join(f"      {idx}. {lm}" for idx, lm in enumerate(curation_landmarks or [], 1)) if curation_landmarks else ""

    channel_block = ""
    if channel_id:
        profile = get_channel_profile(channel_id)
        if profile:
            channel_block = "\n" + profile.format_directorial_guardrails_block() + "\n"

    return f"""You are the Master Visual Director and Senior Cinematic Storyboard Artist for CineAI Studio.
Your role is to author a complete, production-ready, broadcast-grade Screenplay for the "{genre}" channel genre.

{channel_block}
======================================================================
UNIVERSAL CINEMATIC DIRECTIVES (MANDATORY FOR ALL SCENES):
======================================================================
1. PURE PRISTINE UNINHABITED NATURE (ZERO HUMANS, ZERO STRUCTURES):
   - Every scene MUST be 100% uninhabited, wild, raw, primordial nature.
   - Absolutely zero humans, tourists, swimmers, hikers, guides, voices, or faces.
   - Strictly zero modern structures, buildings, cabins, paved roads, vehicles, fences, power lines, boats, or railings.

2. LIVING WALLPAPER & BALANCED CINEMATIC COMPOSITION:
   - Format visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH.
   - In "shot_type", use "wide_panoramic_picturesque".
   - In "visual_prompt", format for high-stability 16:9 landscape framing on a locked tripod with balanced natural depth.
   - In "motion_prompt", ALWAYS anchor with: "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming."

3. SMOOTH HYPNOTIC KINETICS & ANTI-DRIFT CINEMAGRAPH STANDARD:
   - Zero Environmental Warping: Mountains, rock cliffs, forest trees, and the horizon line MUST remain 100% frozen, rigid, and static.
   - Fluid & Atmospheric Animation Only: Animate ONLY the natural dynamic elements (flowing stream water, rolling ocean surf, flickering hearth embers, or gentle rising vapor mist).
   - Anti-Motion-Fatigue Clear Sky Standard: In all relaxation/nature scenes (except explicit rain themes), skies MUST be crystal-clear, cloudless azure skies ("crystal-clear cloudless blue sky, zero clouds, completely clear atmosphere"). STRICTLY PROHIBIT clouds, overcast skies, or drifting clouds, as sky/cloud motion causes visual fatigue in living wallpapers.
   - Domain Specification: Set "water_fluid" for water/rain/falls, "landscape_solid" for mountain/forest vistas, or "cozy_hearth" for campfires.

4. MULTI-MODEL IMAGE PROMPTS ("image_model_configs"):
   - For every scene, you MUST generate model-tailored image prompts inside "image_model_configs" for ALL THREE image models:
     * "flux_dev": Model "fal-ai/flux/dev". Natural balanced landscape phrasing, aspect_ratio: "16:9", guidance_scale: 3.5, num_inference_steps: 28.
     * "flux_pro": Model "fal-ai/flux-pro/v1.1-ultra". Ultra-detailed 8K Hasselblad photorealistic prompt, aspect_ratio: "16:9", raw: true.
     * "zimage": Model "fal-ai/z-image/turbo". Punchy high-contrast photographic prompt, aspect_ratio: "16:9", num_inference_steps: 8.

5. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs"):
   - For every scene, you MUST generate model-specific positive prompts, negative prompts, and optimal API settings inside "model_configs" for:
     * "kling_v1_6_pro": Model "fal-ai/kling-video/v1.6/pro/image-to-video". Directorial action command style.
     * "wan_2_1": Model "fal-ai/wan-i2v". Continuous fluid kinetic phrasing.

6. MANDATORY NEGATIVE PROMPT:
   - For Pure Wilderness: Always include: "clouds, cloudy, overcast sky, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings".
   - For Cozy Living / Bedrooms / Cabins / Walking Tours: Prohibit structural drift, flickering, and artifacts, but DO NOT ban architectural structures: "clouds, cloudy, overcast sky, cumulus, storm clouds, moving clouds, timelapse, camera movement, camera pan, panning, tilt, zoom, morphing architecture, changing furniture, structural drift, flickering, temporal jump, changing lighting, gelatinous water, melting foam, rubbery water, static vertical streaks, falling wire artifacts, artifacts, humans, tourist, clutter, plastic junk, modern electronics".

{specific_rules}

{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{custom_prompt or 'Autonomously curate the greatest world-famous natural landmark on Earth'}"
- Genre: {genre}
- Sub-Genre: {sub_genre}
- Primary Archetype: {archetype}
- Geographic Cluster: {cluster}
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
    "spoken_narration_script": "Mindful, poetic, and educational voiceover narration describing the natural sanctuary, geography, and tranquil atmosphere, paced at 125 wpm.",
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
      "color_temp_kelvin": {color_temp_kelvin},
      "visual_prompt": "A photorealistic, symmetrical 16:9 cinematic landscape view of [Landmark Name], shot on locked tripod. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles.",
      "image_model_configs": {{
        "flux_dev": {{
          "model": "fal-ai/flux/dev",
          "prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing on a locked tripod. In the majestic background, towering terrain rises into a crisp clear sky; in the foreground, pristine natural elements frame the vista. Pristine wilderness, zero buildings, zero tourists.",
          "aspect_ratio": "16:9",
          "guidance_scale": 3.5,
          "num_inference_steps": 28
        }},
        "flux_pro": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. Symmetrical 16:9 cinematic framing, shot on a locked tripod. A breathtaking panoramic landscape view of [Landmark Name]. Pristine untouched wilderness, strictly zero humans, zero modern structures, zero vehicles.",
          "aspect_ratio": "16:9",
          "raw": true
        }},
        "zimage": {{
          "model": "fal-ai/z-image/turbo",
          "prompt": "Stunning photorealistic panoramic landscape of [Landmark Name], 16:9 locked tripod framing, pristine nature, 8k, sharp focus.",
          "aspect_ratio": "16:9",
          "num_inference_steps": 8
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming. Rock cliffs, horizon line, and landscape structure remain 100% frozen and static. Only the natural kinetic elements gently flow in continuous motion with soft vapor mist steadily rising.",
      "motion_negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings",
      "model_configs": {{
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, completely stationary static frame. Landscape structure remains 100% frozen and unmoving. Smooth continuous natural motion, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, flickering, temporal jump, sunny sky, rainbow, changing lighting, parched, frozen ice, stagnant water, artifacts, humans, tourist, boat, railings, buildings"
          }},
          "settings": {{
            "guide_scale": 5.0,
            "num_inference_steps": 30,
            "aspect_ratio": "16:9"
          }}
        }},
        "kling_v1_6_pro": {{
          "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
          "prompts": {{
            "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous natural flow directly matching the source image, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water"
          }},
          "settings": {{
            "mode": "pro",
            "duration": "5",
            "aspect_ratio": "16:9"
          }}
        }}
      }},
      "domain": "water_fluid",
      "duration_seconds": {per_shot_dur}
    }}
  ],
  "publishing": {{
    "ctr_titles": [
      "Authentic High-CTR Title 1 | 4K Living Wallpaper",
      "Authentic High-CTR Title 2 | Deep Nature Relaxation",
      "Authentic High-CTR Title 3 | Pure Soundscape 60 FPS"
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
