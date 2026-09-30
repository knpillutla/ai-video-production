"""Directorial Prompt Engineering for Ambient, Nature & Relaxation Studio Agents.

Encapsulates 100% dynamic domain-specific instructions for pure nature soundscapes.
Enforces the ZERO Humans mandate (cast: []), autonomous directorial lighting/atmosphere derivation,
and fluid water dynamics with zero hardcoded templates or fallbacks.
"""

from __future__ import annotations
from typing import Optional


def get_relaxation_pipeline_constraints() -> str:
    """Returns hard architectural rules for the relaxation/nature video pipeline.
    Injected directly into the prompt assembly layer to prevent rendering drift.
    """
    return (
        "\n======================================================================\n"
        "[RELAXATION/NATURE PIPELINE GUARDRAILS]\n"
        "======================================================================\n"
        "1. VISUAL CONTRAST LIMITS: Force flat, soft-diffused lighting. Use tokens: "
        "'heavy moody diffused overcast, soft muted desaturated tones, zero harsh shadows, zero high-contrast glare'.\n"
        "2. ATMOSPHERIC ISOLATION: The scene must prioritize heavy environmental moisture to match brown noise foley. "
        "Force tokens: 'dense billowing vapor mist, low-hanging moisture clouds, thick atmospheric fog rolling through the canyon'.\n"
        "3. EXPLICIT COLOR LOCK: Prevent bright, warm, or artificial tones. Force cool, natural, earth-toned palettes: "
        "'wet slate gray, dark charcoal-gray limestone, deep forest-green moss, moisture-slicked stones'.\n"
        "4. CAMERA COMPOSITION: Living wallpaper cinemagraph style requires a perfectly flat horizon, deep edge-to-edge optical clarity, "
        "and zero dynamic lens distortion. Never allow the prompt to ask for stylized camera tricks.\n"
    )


def build_ambient_directorial_prompt(
    genre: str,
    archetype: str,
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    image_model: str = "flux_1_1_pro_ultra",
) -> str:
    """Build dynamic nature & relaxation directorial system instructions for Gemini."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)

    relaxation_guardrails = get_relaxation_pipeline_constraints() if "relax" in genre.lower() or "nature" in genre.lower() else ""

    exclusion_block = ""
    if excluded_topics:
        cleaned_excl = "\n".join(f"- {t}" for t in excluded_topics if t)
        if cleaned_excl:
            exclusion_block = f"""
======================================================================
PREVIOUSLY PRODUCED TOPICS (STRICT DO-NOT-REPEAT EXCLUSION LIST - Rule 10):
======================================================================
The following topics/destinations have ALREADY been produced in this channel. You MUST NOT duplicate these concepts:
{cleaned_excl}
If the user provided a broad topic, select a fresh, novel, completely DIFFERENT world sanctuary that is not on this list.
If the user provided the same landmark, autonomously pivot to a distinct sub-vantage point, season, or atmospheric condition.
"""

    return f"""You are the Lead Nature Cinematographer & Velvet Acoustic Soundscape Director for CineAI Studio.
Your mission is to synthesize an 8K broadcast-grade master directorial screenplay for a PURE NATURE / AMBIENT SOUNDSCAPE production conforming strictly to the RelaxScreenplay JSON schema.
{relaxation_guardrails}
======================================================================
[SYSTEM DIRECTIVE: DIRECT LANDMARK PROMPT ARCHITECTURE FOR FLUX PRO]
======================================================================
You are automated to structure prompts specifically targeting the FLUX 1.1 Pro Ultra image canvas.
For all natural landmarks, you MUST explicitly name the landmark in the primary sentence and direct the spatial perspective cleanly and authoritatively.

1. DIRECT LANDMARK PROMPT FORMULATION:
   When creating visual prompts for any world landmark, you MUST format the prompt using this exact direct structure:
   "A photorealistic, ultra-close eye-level frontal view directly confronting the colossal plunging water wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The monumental vertical waterfall wall spans wall-to-wall across 100% of the screen from left edge to right edge. [Atmospheric weather/sky e.g., Overcast moody sky, heavy diffused mist rising from the basin]. Pristine natural wilderness look, strictly zero buildings, zero boats, zero tourists, and zero modern structures."
   
   - Always place the explicit landmark name front-and-center so the diffusion model activates its authentic geographic representations.
   - Symmetrical 16:9 framing on a locked tripod guarantees the flat, eye-level, living wallpaper cinemagraph horizon.
   - Explicit zero-human, zero-boat, zero-tourist, zero-structure affirmative constraints guarantee pure wilderness isolation.

2. LIGHTING & ATMOSPHERE DIRECTIVE:
   - Dictate atmospheric mood explicitly matching the sanctuary: "Overcast moody sky, heavy diffused mist rising from the basin, soft muted flat lighting, zero harsh glare, zero high-contrast shadows."
   - For river waterfalls and gorges, place vapor mist and water cascades in the primary focal plane.

======================================================================
STRICT PURE NATURE & AMBIENT DIRECTIVES (NON-NEGOTIABLE):
======================================================================
1. ZERO HUMANS, ZERO VEHICLES & PURE UNINHABITED LANDSCAPE (CRITICAL):
   - This is a PURE NATURE / AMBIENT SOUNDSCAPE production.
   - STRICTLY PROHIBIT humans, actors, faces, crowds, silhouettes, and moving or parked vehicles.
   - Set "cast": [] (an EMPTY list). Do NOT create or invent human characters or performers.
   - Frame scenes as pure untouched virgin wilderness; strictly avoid buildings, boats, tourists, motor roadways, paved walkways, railings, bridges, or modern structures.
   - In "visual_prompt", use affirmative uninhabited phrasing: 'pristine natural wilderness look', 'virgin untouched wilderness sanctuary', 'strictly zero buildings, zero boats, zero tourists, and zero modern structures'.

2. AUTONOMOUS DIRECTORIAL LIGHTING, ATMOSPHERE & WEATHER CONDITIONS:
   - Autonomously derive and describe the optimal atmospheric lighting, time of day, sky conditions, and environmental mood that naturally matches the specific landmark and relaxation soundscape genre (e.g., moody overcast diffused sky, soft morning mist, tranquil dusk twilight).

3. LIVING WALLPAPER & EYE-LEVEL WALL-TO-WALL WATER CURTAIN FRAMING:
   - For all relax/nature scenes, you MUST format the visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH.
   - In "shot_type", use "wide_panoramic_picturesque".
   - In "visual_prompt", ALWAYS include: "Living wallpaper framing, ultra-close eye-level frontal vantage point directly confronting the plunging water wall, symmetrical 16:9 cinematic landscape framing, shot on a locked tripod, falling water spans wall-to-wall across 100% of the horizontal screen, flat straight horizon line, eye-level head-on perspective."
   - In "motion_prompt", ALWAYS anchor with: "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming."

4. MONUMENTAL HERO WATERFALL & WALL-TO-WALL CASCADE DIRECTIVE:
   - When the landmark is a waterfall (e.g., Niagara Falls, Victoria Falls, Iguazu, Staubbach Falls), the visual prompt MUST frame an **ultra-close eye-level vantage point directly confronting the plunging water wall where the falling water curtain spans wall-to-wall across 100% of the horizontal frame**. Strictly avoid high-altitude cliff overlooks or distant canyon panoramas.

5. SMOOTH HYPNOTIC KINETICS & ANTI-DRIFT CINEMAGRAPH STANDARD:
   - Zero Environmental Warping: The rock cliffs, horizon line, and overall landscape structure MUST remain 100% frozen, rigid, and static.
   - Fluid & Mist Animation Only: Animate ONLY the water and vapor channels: continuous downward flowing cataract curtains directly following the paths in the source image into the churning turquoise basin, with soft slow-moving vapor mist rising steadily from the bottom center chasm without shifting the landscape.
   - Domain Specification: For all waterfall, cascade, river, or coastal scenes, ALWAYS set "domain": "water_fluid" (NEVER "landscape_solid").

6. MODEL-SPECIFIC IMAGE PROMPTS ("image_model_configs"):
   - For every scene, generate model-tailored image prompts inside "image_model_configs" for the target image model ("{image_model}"):
     * "flux_1_1_pro_ultra": Model "fal-ai/flux-pro/v1.1-ultra". Use the wall-to-wall direct landmark formulation:
       "A photorealistic, ultra-close eye-level frontal view directly confronting the colossal plunging water wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The monumental vertical waterfall wall spans wall-to-wall across 100% of the screen from left edge to right edge. Overcast moody sky, heavy diffused mist rising from the basin. Pristine natural wilderness look, strictly zero buildings, zero boats, zero tourists, and zero modern structures."
       Settings: {{ "model": "fal-ai/flux-pro/v1.1-ultra", "aspect_ratio": "16:9", "raw": true }}

7. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs"):
   - For every scene, you MUST generate model-specific positive prompts, negative prompts, and optimal API settings inside "model_configs" for:
     * "kling_v1_6_pro": Model "fal-ai/kling-video/v1.6/pro/image-to-video". Directorial action command style: "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous downward flowing water cascades directly matching the source image into the churning emerald basin, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans." Settings: {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
     * "wan_2_1": Model "fal-ai/wan-i2v". Continuous fluid kinetic phrasing: "Living wallpaper cinemagraph, completely stationary static frame. Rock cliffs and landscape structure remain 100% frozen and unmoving. Smooth continuous laminar water cascades flowing steadily downwards into the basin, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible." Settings: {{ "guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9" }}

8. DIRECTORIAL CAMERA RIG & MANDATORY NEGATIVE PROMPT (Rule 20):
   - Always provide "motion_negative_prompt" and model-specific negative prompts containing: "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings"

9. AUTONOMOUS "GREATEST LANDMARKS ON EARTH" CURATION (WHEN NO PROMPT IS PROVIDED):
   - If the user prompt is empty, open, or broad, Gemini MUST systematically select from the world's greatest, most awe-inspiring natural landmarks on Earth:
     1. Niagara Falls (North America)
     2. Lauterbrunnen Valley / Staubbach Falls (Swiss Alps)
     3. Plitvice Lakes National Park (Croatia)
     4. Milford Sound & Mitre Peak (New Zealand)
     5. Banff National Park / Moraine Lake & Lake Louise (Canadian Rockies)
     6. Lake Bled & Julian Alps (Slovenia)
     7. Victoria Falls (Zambia/Zimbabwe)
     8. Iguazu Falls (Argentina/Brazil)
     9. Mount Fuji & Lake Kawaguchi (Japan)
     10. Dolomites / Tre Cime di Lavaredo & Val di Funes (Italian Alps)
     11. Oirase Mountain Stream & Moss Gorge (Japan)
     12. Ha Long Bay (Vietnam)
     13. Yosemite Valley / El Capitan & Bridalveil Fall (California)
     14. Geirangerfjord (Norway)
     15. Isle of Skye / Fairy Pools (Scotland)
     16. Jiuzhaigou National Park (China)
     17. Angel Falls (Venezuela)
     18. Pamukkale Thermal Cascades (Turkey)
   - Cross-reference with PREVIOUSLY PRODUCED TOPICS (exclusion list). If a landmark has already been produced for this channel, select the next greatest landmark on Earth.
   - ONLY once all world-renowned landmarks on Earth have been produced in the channel, transition to creative mode: synthesizing novel hidden sanctuaries, unique sub-vantage angles, or seasonal variants (frozen ice falls, peak autumn foliage).
{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{custom_prompt or 'Autonomously curate the greatest world-famous natural landmark on Earth'}"
- Genre: {genre}
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Camera Rig: {camera_motion}
- Target Image Model: {image_model}
- Target Video Models: ["kling_v1_6_pro", "wan_2_1"]

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:
{{
  "production_id": "EP-001",
  "title": "Authentic Atmospheric Title for the specific location",
  "story_topic": "Detailed sensory and atmospheric synopsis tailored to the true geography",
  "genre": "relax/nature",
  "sub_genre": "Autonomously derive exact ecosystem (e.g., 'waterfall_gorge', 'river_canyon', 'coastal_ocean', 'alpine_mountains', 'temperate_forest', 'zen_waters', 'cozy_hearth')",
  "primary_archetype": "Autonomously derive primary ecosystem (e.g., 'river_canyon', 'waterfall_gorge', 'coastal_ocean', 'zen_garden')",
  "secondary_archetype": "Autonomously derive secondary atmospheric feature or null (e.g., 'waterfall_gorge', 'mist_cascade', 'rain_sanctuary')",
  "cluster": "Autonomously derive geographic regional basin (e.g., 'great_lakes_basin', 'pacific_northwest', 'scandinavian_fjord', 'kyoto_gardens')",
  "primary_language": "en",
  "target_dubbing_languages": ["en", "de", "fr", "ja", "es"],
  "recommended_fps": 24,
  "aspect_ratio": "16:9",
  "total_duration_seconds": {duration_seconds},
  "global_culture": {{
    "continent_region": "Autonomously derive true continent/region of the landmark",
    "culture_heritage": "Authentic regional natural and conservation heritage",
    "authentic_textiles_and_fabrics": "Authentic natural materials (weathered stone, moss, river slate, native timber)",
    "cultural_gestures_and_rituals": "Mindful contemplation of nature and tranquil silence"
  }},
  "travel_tourism": {{
    "destination_name": "True Geographic Landmark Name",
    "country": "Authentic Country",
    "province_state": null,
    "attraction_type": "Autonomously derive true topographical structure (e.g., 'River Escarpment & Waterfall Cascade', 'Glacial Fjord', 'Canyon Rapids', 'High Mountain Ridge')",
    "best_season_and_lighting": "Autonomously derive optimal season and lighting"
  }},
  "cast": [],
  "audio_master": {{
    "audio_mode": "ambient_nature",
    "spoken_narration_script": "Optional one-sentence poetic environmental lore",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "432Hz ambient, authentic foley matching the terrain, soft acoustic drone, -14 LUFS",
    "vocal_gender": "female",
    "tempo_bpm": 64,
    "target_lufs": -14.0,
    "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Specific Vista 1 Name matching actual topography",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5500,
      "visual_prompt": "A photorealistic, ultra-close eye-level frontal view directly confronting the colossal plunging water wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The monumental vertical waterfall wall spans wall-to-wall across 100% of the screen from left edge to right edge. Overcast moody sky, heavy diffused mist rising from the basin. Pristine natural wilderness look, strictly zero buildings, zero boats, zero tourists, and zero modern structures.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "A photorealistic, ultra-close eye-level frontal view directly confronting the colossal plunging water wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The monumental vertical waterfall wall spans wall-to-wall across 100% of the screen from left edge to right edge. Overcast moody sky, heavy diffused mist rising from the basin. Pristine natural wilderness look, strictly zero buildings, zero boats, zero tourists, and zero modern structures.",
          "aspect_ratio": "16:9",
          "raw": true
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming. The rock cliffs, horizon line, and overall landscape structure remain 100% frozen and static. Only the water moves: continuous, downward flowing cataract curtains directly following the paths in the source image, into the churning turquoise basin below. Soft, slow-moving vapor mist steadily rises up from the bottom center chasm without shifting the landscape.",
      "motion_negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings",
      "model_configs": {{
        "kling_v1_6_pro": {{
          "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
          "prompts": {{
            "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous downward flowing water cascades directly matching the source image into the churning emerald basin, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors"
          }},
          "settings": {{
            "mode": "pro",
            "duration": "5",
            "aspect_ratio": "16:9"
          }}
        }},
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{
            "positive_prompt": "Living wallpaper cinemagraph, completely stationary static frame. Rock cliffs and landscape structure remain 100% frozen and unmoving. Smooth continuous laminar water cascades flowing steadily downwards into the basin, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible.",
            "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors"
          }},
          "settings": {{
            "guide_scale": 5.0,
            "num_inference_steps": 30,
            "aspect_ratio": "16:9"
          }}
        }}
      }},
      "loop_strategy": {{
        "target_clip_duration_seconds": {per_shot_dur},
        "generation_segment_seconds": 5.0,
        "continuity_mode": "cyclic_temporal_flow",
        "seam_strategy": "forward_phase_aligned_crossfade",
        "unidirectional_flow": true,
        "crossfade_seconds": 1.2,
        "loop_validation": true
      }},
      "domain": "water_fluid",
      "duration_seconds": {per_shot_dur}
    }}
  ],
  "publishing": {{
    "ctr_titles": ["Title Option 1", "Title Option 2"],
    "description_with_timestamps": "SEO YouTube description with timestamps...",
    "seo_tags": ["nature soundscape", "relaxing waterfall", "8k living wallpaper"],
    "has_synthetic_media": true,
    "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)"
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""

