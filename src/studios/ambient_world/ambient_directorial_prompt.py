"""Directorial Prompt Engineering for Ambient, Nature & Relaxation Studio Agents.

Encapsulates 100% dynamic domain-specific instructions for pure nature soundscapes.
Enforces the ZERO Humans mandate (cast: []), autonomous directorial lighting/atmosphere derivation,
and fluid water dynamics with zero hardcoded templates or fallbacks.
"""

from __future__ import annotations
from typing import Optional


def get_relaxation_pipeline_constraints(archetype: str = "") -> str:
    """Returns dynamic architectural guardrails for the relaxation/nature video pipeline.
    Adapts lighting and atmospheric constraints to the ecosystem archetype.
    """
    if "alpine" in archetype.lower() or "mountain" in archetype.lower():
        return (
            "\n======================================================================\n"
            "[ALPINE MOUNTAIN & NATURE PIPELINE GUARDRAILS]\n"
            "======================================================================\n"
            "1. CRISP NATURAL ATMOSPHERE: Prioritize majestic alpine clarity with towering snow-capped peaks, "
            "vibrant wildflower meadows, and crystal-clear glacial streams.\n"
            "2. BALANCED NATURAL ILLUMINATION: Crisp morning or afternoon daylight (5500K-6000K), soft alpine glow, "
            "zero harsh artificial lens flare blowouts.\n"
            "3. CAMERA COMPOSITION: 16:9 panoramic landscape framing, locked tripod, flat straight horizon line.\n"
        )
    return (
        "\n======================================================================\n"
        "[RELAXATION/NATURE PIPELINE GUARDRAILS]\n"
        "======================================================================\n"
        "1. NATURAL DIFFUSED ILLUMINATION: Soft, balanced natural lighting, zero artificial harsh glare.\n"
        "2. ECOSYSTEM AUTHENTICITY: Depict genuine geographic topography, vegetation, and water dynamics.\n"
        "3. CAMERA COMPOSITION: Living wallpaper cinemagraph style, locked tripod, deep edge-to-edge optical clarity.\n"
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
    google_search_enabled: bool = False,
) -> str:
    """Build dynamic nature & relaxation directorial system instructions for Gemini."""
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)
    landmark_research_directive = (
      "Use Google Search grounding alongside built-in geographic knowledge to verify current facts and destination interest. "
      "Do not claim a place is trending unless the search evidence supports it."
      if google_search_enabled else
      "Use built-in geographic and cultural knowledge to choose an established notable destination. "
      "Do not claim current trends or real-time popularity; no web search is enabled for this request."
    )
    concept_anchor = custom_prompt or (
      "No user prompt supplied; select a notable destination matching the genre and archetype using grounded search."
      if google_search_enabled else
      "No user prompt supplied; select a notable destination matching the genre and archetype using built-in knowledge."
    )

    relaxation_guardrails = get_relaxation_pipeline_constraints(archetype) if "relax" in genre.lower() or "nature" in genre.lower() else ""

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

1. DYNAMIC ECOSYSTEM & LANDMARK PROMPT FORMULATION:
   When creating visual prompts for world landmarks and nature sanctuaries, format the prompt dynamically based on the ecosystem archetype:
   - **Alpine Mountains & Valleys (e.g., Swiss Alps, Dolomites, Canadian Rockies, Mount Fuji):**
     "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into a crisp clear sky; in the foreground and midground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil crystal-clear glacial mountain stream. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles, and zero modern structures."
   - **Alpine Lakes & Fjords (e.g., Lake Louise, Lake Bled, Geirangerfjord, Milford Sound):**
     "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Glassy mirror-still turquoise waters perfectly reflect the towering forested cliffs and snow-capped peaks under soft morning light. Pristine untouched wilderness, strictly zero boats, zero buildings, zero tourists, and zero structures."
   - **Monumental Waterfalls (e.g., Niagara Falls, Victoria Falls, Iguazu Falls):**
     "A photorealistic, eye-level frontal view confronting the monumental cascading water wall of [Landmark Name]. Symmetrical 16:9 cinematic landscape framing, shot on a locked tripod. The powerful roaring waterfall cascades down dark volcanic stone into a misty churning turquoise basin with soft vapor rising. Pristine natural wilderness, strictly zero buildings, zero boats, zero tourists, and zero structures."
   - **Coastal Ocean & Beach Campfire (e.g., Big Sur, Oregon Coast, Silent Hearth):**
     "A photorealistic, wide eye-level view of a cozy natural stone campfire burning directly on the wet pebble sand at [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Warm glowing wood embers crackle under an open twilight sky while gentle rhythmic ocean waves roll and surge along the shoreline. 100% open-air outdoor beach, strictly zero indoor rooms, zero sofas, zero interior walls, zero ceilings, zero glass windows."
   - **Temperate Forests, Gorges & Moss Streams (e.g., Oirase Stream, Fairy Pools, Olympic Forest):**
     "A photorealistic, eye-level landscape view of the lush ancient moss forest and tranquil babbling river at [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Crystal clear emerald water flows gently over moisture-slicked river stones and vibrant green moss beds under soft diffused canopy light. Pristine untouched wilderness, strictly zero buildings, zero tourists, zero roads, and zero structures."

2. LIGHTING & ATMOSPHERE DIRECTIVE:
   - Autonomously derive and dictate atmospheric mood matching the ecosystem (e.g., crisp alpine morning light, soft diffused forest mist, tranquil twilight blue hour, or moody overcast).
   - Maintain natural balanced lighting without artificial harsh glare or extreme color oversaturation.

======================================================================
STRICT PURE NATURE & AMBIENT DIRECTIVES (NON-NEGOTIABLE):
======================================================================
1. ZERO HUMANS, ZERO VEHICLES & PURE UNINHABITED LANDSCAPE (CRITICAL):
   - This is a PURE NATURE / AMBIENT SOUNDSCAPE production.
   - STRICTLY PROHIBIT humans, actors, faces, crowds, silhouettes, and moving or parked vehicles.
   - Set "cast": [] (an EMPTY list). Do NOT create or invent human characters or performers.
   - Frame scenes as pure untouched virgin wilderness; strictly avoid buildings, boats, tourists, motor roadways, paved walkways, railings, bridges, or modern structures.
   - In "visual_prompt", use affirmative uninhabited phrasing: 'pristine natural wilderness look', 'virgin untouched wilderness sanctuary', 'strictly zero buildings, zero boats, zero tourists, and zero modern structures'.

2. LIVING WALLPAPER & BALANCED CINEMATIC COMPOSITION:
   - For all relax/nature scenes, format the visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH.
   - In "shot_type", use "wide_panoramic_picturesque".
   - In "visual_prompt", format for high-stability 16:9 landscape framing on a locked tripod with balanced natural depth.
   - In "motion_prompt", ALWAYS anchor with: "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming."

3. SMOOTH HYPNOTIC KINETICS & ANTI-DRIFT CINEMAGRAPH STANDARD:
   - Zero Environmental Warping: Mountains, rock cliffs, forest trees, and the horizon line MUST remain 100% frozen, rigid, and static.
   - Fluid & Atmospheric Animation Only: Animate ONLY the natural dynamic elements (flowing stream water, rolling ocean surf, flickering hearth embers, or gentle rising vapor mist).
   - Anti-Motion-Fatigue Clear Sky Standard: In all relaxation/nature vistas (alpine mountains, valleys, meadows, fjords, lakes, waterfalls, hearths), the sky MUST be a crystal-clear, cloudless azure sky ("crystal-clear cloudless blue sky, zero clouds, completely clear atmosphere"). STRICTLY PROHIBIT clouds, cumulus formations, overcast skies, and drifting clouds, as sky/cloud motion causes visual fatigue in living wallpapers.
   - Domain Specification: Set "water_fluid" for water/rain/falls, "landscape_solid" for mountain/forest vistas, or "cozy_hearth" for campfires.

4. MODEL-SPECIFIC IMAGE PROMPTS ("image_model_configs"):
   - For every scene, generate model-tailored image prompts inside "image_model_configs" for the target image model ("{image_model}"):
     * "{image_model}": Use the dynamic ecosystem formulation derived in Section 1 matching the exact terrain (e.g. Alpine Mountains & Valleys for mountains, Panoramic Lakes for fjords/lakes, Ocean Beach for campfires, Cascades for waterfalls).
       Settings: {{ "model": "fal-ai/flux-pro/v1.1-ultra", "aspect_ratio": "16:9", "raw": true }}

5. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs"):
   - For every scene, you MUST generate model-specific positive prompts, negative prompts, and optimal API settings inside "model_configs" for:
     * "kling_v1_6_pro": Model "fal-ai/kling-video/v1.6/pro/image-to-video". Directorial action command style: "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous downward flowing water cascades directly matching the source image into the churning emerald basin, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans." Settings: {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
     * "wan_2_1": Model "fal-ai/wan-i2v". Continuous fluid kinetic phrasing: "Living wallpaper cinemagraph, completely stationary static frame. Rock cliffs and landscape structure remain 100% frozen and unmoving. Smooth continuous laminar water cascades flowing steadily downwards into the basin, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible." Settings: {{ "guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9" }}

8. DIRECTORIAL CAMERA RIG & MANDATORY NEGATIVE PROMPT (Rule 20):
   - Always provide "motion_negative_prompt" and model-specific negative prompts containing: "clouds, cloudy, overcast sky, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings"

9. AUTONOMOUS LANDMARK DISCOVERY (WHEN NO PROMPT IS PROVIDED):
  - Use the supplied genre and archetype to choose a real, geographically accurate destination; do not substitute a generic or unrelated default location.
  - {landmark_research_directive}
  - Select one destination and derive a fresh title and story around its authentic landscape, while excluding previously produced topics listed above.
  - If the user supplied a prompt, treat it as the creative anchor and do not replace it with an unrelated destination.
{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{concept_anchor}"
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
      "visual_prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil crystal-clear glacial stream. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles, and zero modern structures.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil crystal-clear glacial stream. Pristine natural wilderness, strictly zero buildings, zero tourists, zero vehicles, and zero modern structures.",
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

