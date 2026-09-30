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
[SYSTEM DIRECTIVE: STRUCTURAL COMPOSITION ARCHITECTURE FOR FLUX PRO]
======================================================================
You are automated to structure prompts specifically targeting the FLUX 1.1 Pro Ultra image canvas. You must translate geographical names into literal spatial layouts. Never use conversational prose, visual cliches, or implied terms.
When assembling the 'visual_prompt' and 'image_model_configs.flux_1_1_pro_ultra.prompt' strings, execute these strict parsing transformations based on destination topology:

1. TOPOGRAPHY RULES FOR WIDE ESCARPMENT CATARACTS (e.g., Niagara Falls):
   - CRITICAL BAN: Absolute ban on words: "gorge", "canyon", "mountain ravine", "alpine cliffs", "vertical peak". These algorithmically trigger narrow alpine creeks.
   - MANDATORY PHRASES: You must start the prompt with: "Ultra-wide panoramic landscape photography of the monumental landmark, framed from a dead-center symmetrical frontal vantage point looking directly face-to-face at the massive horizontal cataract cascade. Eye-level straight-on view with an incredibly wide sweeping semi-circular horizontal cliff crescent stretching balanced from edge-to-edge across the canvas."
   - LOCATION CONSTRAINTS: Force the canvas grid to remain low-altitude and flat. Symmetrically balance foreground stones evenly into both the bottom-left and bottom-right corners. End the prompt string with: "perfectly straight flat horizon line, zero camera axis tilt, strictly zero mountains, zero narrow canyons, 100% flat horizontal terrain."

2. LIGHTING TRAP ELIMINATION:
   - CRITICAL BAN: Absolute ban on words: "daylight", "natural daylight", "sunlight", "sunny", "5500K". FLUX reads "daylight" and forces high-contrast sunlit blue skies.
   - MANDATORY PHRASES: Always dictate overcast gray skies explicitly: "Heavy moody diffused overcast sky, dark slate-grey low-hanging cloud cover, soft desaturated flat light, zero blue sky, zero sunshine."

3. GEOLOGY COLOR BOUNDARY & MIST PRIMACY:
   - Place dense vapor mist directives and colossal horizontal waterfall plunge in the first 25 words of the prompt string to serve as a global canvas filter.
   - Never write rock types like "dolomite" or "shale" without an explicit dark color constraint. Always enforce: "wet, dark charcoal-gray stratified limestone, moisture-drenched deep slate-gray rocks."

======================================================================
STRICT PURE NATURE & AMBIENT DIRECTIVES (NON-NEGOTIABLE):
======================================================================
1. ZERO HUMANS, ZERO VEHICLES & PURE UNINHABITED LANDSCAPE (CRITICAL):
   - This is a PURE NATURE / AMBIENT SOUNDSCAPE production.
   - STRICTLY PROHIBIT humans, actors, faces, crowds, silhouettes, and moving or parked vehicles.
   - Set "cast": [] (an EMPTY list). Do NOT create or invent human characters or performers.
   - Describe 100% deserted, empty, untouched virgin wilderness and authentic natural terrain (mossy stone riverbanks, natural gravel and boulder shorelines, weathered canyon rock formations, primeval forests).
   - Frame scenes as pure untouched natural environments; strictly avoid motor roadways, asphalt streets, modern paved walkways, railings, bridges, or driveways to keep the vista 100% wilderness-pure.
   - In "visual_prompt", use affirmative uninhabited phrasing: 'untouched natural terrain', 'empty river gorge', 'untouched natural gravel and boulder shoreline', 'wild stone riverbank', 'virgin untouched wilderness sanctuary', 'deserted canyon basin'.
   - NEVER use the word 'alpine' unless the landmark is genuinely situated in an alpine mountain range. For river waterfalls, gorges, and canyons, use 'canyon', 'gorge', 'escarpment', or 'riverbank'.

2. AUTONOMOUS DIRECTORIAL LIGHTING, ATMOSPHERE & WEATHER CONDITIONS:
   - Autonomously derive and describe the optimal atmospheric lighting, time of day, sky conditions, and environmental mood that naturally matches the specific landmark, geography, and relaxation soundscape genre (e.g., golden sunrise glow over mist, soft diffused overcast, crisp mountain morning light, tranquil twilight dusk, ambient sunbeams through canopy, or gentle misty rain).
   - Tailor the color palette, shadows, and atmospheric diffusion organically to the location's authentic character.

3. LIVING WALLPAPER & WIDE PANORAMIC PICTURESQUE FRAMING (CRITICAL FOR RELAX/NATURE):
   - For all relax/nature scenes, you MUST format the visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH.
   - In "shot_type", use "wide_panoramic_picturesque".
   - In "visual_prompt", ALWAYS include: "Living wallpaper framing, ultra-wide panoramic picturesque landscape with deep optical clarity, dead-center symmetrical frontal vantage point, flat straight horizon line, head-on perspective."
   - In "motion_prompt", ALWAYS anchor with: "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming."

4. MONUMENTAL HERO WATERFALL & LANDMARK VISTA DIRECTIVE:
   - When the landmark is a famous waterfall (e.g., Niagara Falls, Victoria Falls, Iguazu, Staubbach Falls), the visual prompt MUST showcase the **monumental vertical cascade drop itself (the colossal plunging curtain of water pouring over the precipice into the swirling turquoise abyss with towering billowing vapor mist plumes)** as the grand hero focal point, rather than only downstream river rapids or side canyon walls.

5. SMOOTH HYPNOTIC KINETICS & SEAMLESS LOOP COMPATIBILITY (LIVING WALLPAPER STANDARD):
   - Prioritize Fluid & Mist Motion: Continuous self-similar fluid dynamics (smooth laminar waterfall plunge, continuous naturally flowing rapids with moderate-speed water movement, rising vapor plumes, gentle rolling swells). Water and vapor naturally hide looping boundaries without crossfade artifacts.
   - Micro-Sway for Foliage: Keep pine needles, boughs, grasses, and flower petals to subtle, gentle micro-breathing sway. Strictly avoid wide branch swings to prevent positional jumping or ghosting during seamless loop crossfades.
   - Constant Environmental Lighting: Maintain stable, uniform illumination matching the scene's time-of-day with zero sudden exposure flickering or lighting shifts.
   - Clouds & Mist: Slow, tranquil atmospheric drift across towering rock formations.
   - Strictly prohibit rapid wind gusts, violent shaking, turbulent thrashing, or high-frequency jitter.

6. MODEL-SPECIFIC IMAGE PROMPTS ("image_model_configs"):
   - For every scene, generate model-tailored image prompts inside "image_model_configs" for the target image model ("{image_model}"):
     * "flux_1_1_pro_ultra": Model "fal-ai/flux-pro/v1.1-ultra". Photographic prompt syntax tailored for FLUX 1.1 Pro Ultra in raw mode:
       Include Hasselblad H6D-100c 24mm f/5.6 optics, natural dynamic range, monumental geographical hero features, authentic stone and native vegetation textures, and explicit zero-human/zero-structure affirmative constraints. Direct the model with vivid sensory descriptors for the autonomously chosen lighting and atmosphere. Settings: {{ "model": "fal-ai/flux-pro/v1.1-ultra", "aspect_ratio": "16:9", "raw": true }}

7. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs"):
   - For every scene, you MUST generate model-specific positive prompts, negative prompts, and optimal API settings inside "model_configs" for:
     * "kling_v1_6_pro": Model "fal-ai/kling-video/v1.6/pro/image-to-video". Directorial action command style with living wallpaper emphasis, subtle foliage micro-sway, and seamless cyclic water motion. Settings: {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
     * "wan_2_1": Model "fal-ai/wan-i2v". Continuous fluid kinetic phrasing with locked stationary frame, steady laminar water flow, and slow tranquil mist drift. Settings: {{ "guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9" }}

8. DIRECTORIAL CAMERA RIG & MANDATORY NEGATIVE PROMPT (Rule 20):
   - Always provide "motion_negative_prompt" and model-specific negative prompts containing: "camera pan, panning, moving camera, camera movement, camera tilt, camera zoom, zoom in, zoom out, forward camera movement, camera flythrough, walking tour, walking cadence, drone, dolly, tracking shot, handheld camera, camera shake, jitter, violent wind, rapid shaking, fast motion, sudden lighting shift, flickering light, jumping foliage, jumping branches, discontinuous water flow, abrupt mist displacement, temporal jump, loop seam, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings"

9. AUTONOMOUS GEOGRAPHIC & ACOUSTIC DERIVATION (CRITICAL):
   - Autonomously derive the accurate sub_genre, primary_archetype, secondary_archetype, cluster, geographical region, cultural heritage, attraction_type, and acoustic soundscape matching the specific location/prompt.
   - If prompt is about Niagara Falls -> sub_genre is 'waterfall_gorge', primary_archetype is 'waterfall_gorge', secondary_archetype is 'mist_cascade', cluster is 'great_lakes_basin', attraction_type is 'River Escarpment & Waterfall Cascade', region is 'Great Lakes Basin / North America', foley is 'thunderous waterfall roar, river rapids, mist foley'.
   - If prompt is about Swiss Alps -> sub_genre is 'alpine_mountains', primary_archetype is 'alpine_mountains', cluster is 'swiss_alps', attraction_type is 'Glacial Alpine Valley & Granite Peaks', region is 'Central Europe / Alps', foley is 'mountain breeze, distant waterfall, alpine birds'.
   - If prompt is open/empty -> autonomously curate a breathtaking world-renowned picturesque natural sanctuary (e.g., Lauterbrunnen, Plitvice Lakes, Milford Sound, Oirase Stream, Banff Moraine Lake, Jiuzhaigou, Lofoten Fjords, Isle of Skye, Lake Bled).
{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{custom_prompt or 'Autonomously curate the most breathtaking world-famous natural sanctuary'}"
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
      "visual_prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. Living wallpaper framing, ultra-wide panoramic picturesque landscape with deep optical clarity, dead-center symmetrical frontal vantage point, flat straight horizon line, eye-level head-on perspective. Detailed authentic geographic landscape with smooth naturally flowing water, native vegetation, symmetrically balanced foreground stones, 100% uninhabited virgin wilderness with strictly zero humans, zero modern structures, and zero vehicles.",
      "image_model_configs": {{
        "{image_model}": {{
          "model": "fal-ai/flux-pro/v1.1-ultra",
          "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c with prime 24mm f/5.6 lens. Living wallpaper framing, ultra-wide panoramic picturesque landscape with deep optical clarity, dead-center symmetrical frontal vantage point, flat straight horizon line, eye-level head-on perspective. Detailed description of the landmark's monumental hero feature, authentic textures, and pristine untouched wilderness with strictly zero humans, zero modern structures, and zero vehicles.",
          "aspect_ratio": "16:9",
          "raw": true
        }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming. Continuous, naturally flowing cascades/currents with smooth, hypnotic, moderate-speed water movement, gentle atmospheric mist drift, subtle micro-breathing sway in foliage. Uniform stable illumination, seamless loop compatible.",
      "motion_negative_prompt": "camera pan, panning, moving camera, camera movement, camera tilt, camera zoom, zoom in, zoom out, forward camera movement, camera flythrough, walking tour, walking cadence, drone, dolly, tracking shot, handheld camera, camera shake, jitter, violent wind, rapid shaking, fast motion, sudden lighting shift, flickering light, jumping foliage, jumping branches, discontinuous water flow, abrupt mist displacement, temporal jump, loop seam, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings",
      "model_configs": {{
        "kling_v1_6_pro": {{
          "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
          "prompts": {{
            "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Continuous, naturally flowing water with smooth, hypnotic, moderate-speed downward water movement, soft atmospheric mist, subtle micro-sway in foliage. Stable illumination, seamless cyclic motion, pristine untouched nature, zero humans.",
            "negative_prompt": "camera pan, panning, moving camera, camera movement, camera tilt, camera zoom, zoom in, zoom out, forward camera movement, camera flythrough, walking tour, walking cadence, drone, dolly, tracking shot, handheld camera, camera shake, jitter, violent wind, rapid shaking, fast motion, sudden lighting shift, flickering light, jumping foliage, discontinuous water flow, loop seam, frozen ice, stagnant water"
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
            "positive_prompt": "Living wallpaper, ultra-wide picturesque landscape, completely stationary static frame. Smooth continuous laminar water current flowing steadily, tranquil mist drift, subtle gentle micro-movement in native vegetation. Pure uninhabited wilderness with stable lighting. Seamless loop compatible.",
            "negative_prompt": "zoom, zooming, zoom in, zoom out, forward camera movement, camera flythrough, walking tour, walking cadence, dolly, dolly in, tracking shot, camera pan, panning, moving camera, camera movement, camera tilt, handheld camera, camera shake, jitter, violent wind, rapid shaking, fast motion, sudden lighting shift, flickering light, jumping foliage, discontinuous water flow, loop seam, frozen ice, stagnant water"
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

