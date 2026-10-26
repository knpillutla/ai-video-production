"""Directorial Prompt Engineering for Ambient, Nature & Relaxation Studio Agents."""
from __future__ import annotations
from typing import Optional


def get_relaxation_pipeline_constraints(archetype: str = "") -> str:
    """Returns dynamic architectural guardrails for the relaxation/nature video pipeline."""
    arch_l = archetype.lower()
    if any(w in arch_l for w in ["starlight", "midnight", "hearth"]):
        return (
            "\n[DESERT & STARLIT HEARTH PIPELINE GUARDRAILS]\n"
            "1. DESERT MANDATE: Rolling golden dunes under starlit midnight sky with Milky Way.\n"
            "2. WARM CAMPFIRE: Open-air luxury Bedouin pavilion on dune ridge, glowing lanterns, stone campfire.\n"
            "3. HYPNOTIC SERENITY: Warm lantern glow (2200K) against indigo cosmos, rock-steady locked tripod.\n"
        )
    if any(w in arch_l for w in ["desert", "dune", "tent", "glamping", "daytime"]):
        return (
            "\n[LUXURY DESERT TENT & DAYTIME DUNES GUARDRAILS]\n"
            "1. DAYTIME DESERT: Vast golden sand dunes in natural daytime sunlight (5500K) under clear blue sky.\n"
            "2. INSIDE-OUT TENT FRAMING: Shaded pavilion framing view, sheer cream linen curtains, rich Berber kilims.\n"
            "3. DAYTIME CRISP ILLUMINATION: 5500K natural daylight, sun caustics on sand ripples, zero harsh glare.\n"
            "4. AUDIO MASTER: 432Hz ultra-slow (50 BPM) desert soundbath, airy wooden ney flute, breeze, -21 LUFS.\n"
        )
    if "alpine" in arch_l or "mountain" in arch_l:
        return (
            "\n[ALPINE MOUNTAIN & NATURE PIPELINE GUARDRAILS]\n"
            "1. CRISP NATURAL ATMOSPHERE: Majestic alpine peaks, vibrant wildflower meadows, crystal glacial streams.\n"
            "2. BALANCED NATURAL ILLUMINATION: Crisp daylight (5500K-6000K), soft alpine glow, zero flare blowouts.\n"
            "3. CAMERA COMPOSITION: 16:9 panoramic landscape framing, locked tripod, flat straight horizon line.\n"
        )
    return (
        "\n[RELAXATION/NATURE PIPELINE GUARDRAILS]\n"
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
    tier: str = "balanced",
) -> str:
    """Build dynamic nature & relaxation directorial system instructions for Gemini."""
    clean_tier = (tier or "balanced").strip().lower()
    is_low_cost = clean_tier in ("low_cost", "tier_0", "local")
    per_shot_dur = round(duration_seconds / max(1, num_shots), 1)
    landmark_research_directive = (
        "Use Google Search grounding alongside built-in geographic knowledge to verify current facts and destination interest. "
        "Do not claim a place is trending unless the search evidence supports it."
        if google_search_enabled else
        "Use built-in geographic and cultural knowledge to choose an established notable destination. "
        "Do not claim current trends or real-time popularity; no web search is enabled for this request."
    )
    arch_l = archetype.lower()
    if any(w in arch_l for w in ["tent", "glamping", "daytime"]):
        concept_anchor = custom_prompt or "Luxury Desert Glamping Tent Daytime View: Masterpiece 4K view looking outward from inside an ultra-luxury desert tent onto vast golden sand dunes in natural 5500K daytime sunlight, sheer cream linen curtains billowing, low brass tea table, clear blue sky, zero night, zero campfire"
    elif "desert" in arch_l or "dune" in arch_l:
        concept_anchor = custom_prompt or "Desert Starlit Campfire & Bedouin Pavilion: Open-air luxury Bedouin pavilion on high sand dunes at midnight, Persian rugs, glowing brass Moroccan lanterns, crackling campfire embers, starlit Milky Way sky"
    else:
        concept_anchor = custom_prompt or (
            "No user prompt supplied; select a notable destination matching the genre and archetype using grounded search."
            if google_search_enabled else "No user prompt supplied; select a notable destination matching the genre and archetype using built-in knowledge."
        )

    relaxation_guardrails = get_relaxation_pipeline_constraints(archetype) if "relax" in genre.lower() or "nature" in genre.lower() else ""

    exclusion_block = ""
    if excluded_topics:
        cleaned_excl = "\n".join(f"- {t}" for t in excluded_topics if t)
        if cleaned_excl:
            exclusion_block = (
                "\n======================================================================\n"
                "PREVIOUSLY PRODUCED TOPICS (STRICT DO-NOT-REPEAT EXCLUSION LIST - Rule 10):\n"
                "======================================================================\n"
                f"You MUST NOT duplicate these concepts:\n{cleaned_excl}\n"
                "Autonomously pivot to a fresh, distinct destination, season, or perspective.\n"
            )

    is_balanced = clean_tier in ("balanced", "standard", "default", "normal")
    if is_low_cost:
        motion_contract = (
            "3. TIER-0 / LOW-COST LOCKED TRIPOD KEN BURNS DIRECTORIAL CONTRACT ($0.00 COMPUTE):\n"
            '   - MANDATORY "motion_type": "ken_burns" for 100% of scenes.\n'
            '   - STRICT LOCKED TRIPOD MANDATE: Relaxation format strictly mandates a FIXED LOCKED TRIPOD overlooking scenery.\n'
            f'   - "camera_movement": strictly stationary hold: [{{"stage": 1, "duration": {per_shot_dur}, "movements": ["stay"]}}]. Strictly ZERO panning, tilting, orbiting, or zooming.\n'
            '   - "camera_rig": strictly "locked_tripod_telephoto".\n'
            '   - "motion_rationale": "Fixed locked tripod overlooking natural scenery via local 4K steady hold ($0.00 compute)."'
        )
        ex_motion_type = "ken_burns"
        ex_motion_engine = "local_steady_hold"
        ex_camera_movement = f'[{{ "stage": 1, "duration": {per_shot_dur}, "movements": ["stay"] }}]'
    elif is_balanced:
        motion_contract = (
            "3. BALANCED TIER DIRECTORIAL CONTRACT (80% LOCAL STEADYCAM / 20% AI DIFFUSION COST SPLIT):\n"
            "   - MANDATORY 80/20 COST-OPTIMIZATION SPLIT ACROSS SCENES:\n"
            '     * 80% OF SCENES (e.g. 4 of 5 scenes) MUST USE "motion_type": "ken_burns", "recommended_model": "local_drone".\n'
            '       CRITICAL ZERO-MOTION IMAGE PROMPT MANDATE (COST $0.00): Visual prompts for these 80% scenes MUST depict STILL, TIMELESS scenery with ZERO moving elements (STRICTLY NO flying birds, NO crashing ocean waves or surf, NO moving vehicles/boats, NO walking people, NO active animals, NO turbulent rushing water). Use glassy mirror-still reflections, towering peaks, ancient architecture, quiet meadows. Camera rig strictly "locked_tripod_telephoto", camera_movement: [{"stage": 1, "duration": ' + str(per_shot_dur) + ', "movements": ["stay"]}]. Local 4K steadycam hold ($0.00 compute)!\n'
            '     * 20% OF SCENES (e.g. 1 of 5 scenes) MUST USE "motion_type": "ai_diffusion", "recommended_model": "kling_v3_4k" (or "wan_2_1").\n'
            '       DYNAMIC HERO MOTION: Reserve AI diffusion exclusively for hero scenes with dynamic fluid motion (crashing ocean surf, flying birds soaring overhead, cascading waterfall impact, swirling campfire embers, rustling canopy in storm).'
        )
        ex_motion_type = "ken_burns"
        ex_motion_engine = "local_steady_hold"
        ex_camera_movement = f'[{{ "stage": 1, "duration": {per_shot_dur}, "movements": ["stay"] }}]'
    else:
        motion_contract = (
            f"3. AI DIFFUSION LIVING WALLPAPER DIRECTORIAL CONTRACT (TIER: {clean_tier.upper()}):\n"
            '   - MANDATORY "motion_type": "ai_diffusion" for 100% of scenes.\n'
            '   - LIVING WALLPAPER CINEMAGRAPH: Symmetrical 16:9 framing on a locked tripod with living AI video diffusion animating water currents, waves, swaying flora, or drifting mist.\n'
            '   - "camera_movement": strictly "locked_stationary_cinemagraph".\n'
            '   - "camera_rig": strictly "locked_tripod_telephoto".\n'
            '   - "motion_rationale": "Living wallpaper cinemagraph via AI diffusion for natural fluid/foliage kinematics."\n'
            '   - Model Configs: Generate model-specific configs for "wan_2_1" and "kling_v1_6_pro".'
        )
        ex_motion_type = "ai_diffusion"
        ex_motion_engine = "neural_diffusion"
        ex_camera_movement = '"locked_stationary_cinemagraph"'

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
   - **Desert Sanctuaries, Dunes & Luxury Glamping Tents (e.g., Sahara, Namib, Arabian Desert):**
     * Daytime Luxury Tent: "A photorealistic, wide panoramic view looking outward through the open entrance of an ultra-luxury desert glamping pavilion onto vast majestic golden sand dunes in natural daytime sunlight. Symmetrical 16:9 framing on a locked tripod. Sheer cream linen draperies billow gently at the frame edges. Inside the shaded pavilion, rich hand-woven Berber kilim rugs, plush floor cushions, and a low carved wooden table with an ornate Moroccan brass tea set. Outside, sculptured undulating golden sand dunes with delicate wind ripples stretch endlessly under a crystal-clear cerulean blue sky in balanced 5500K natural daylight. Strictly zero tourists, zero footprints, zero modern clutter, zero vehicles."
     * Starlit Campfire Pavilion: "A photorealistic, wide panoramic landscape view of a luxury open-air Bedouin desert pavilion on a high sand dune ridge under a starry midnight sky. Symmetrical 16:9 cinematic framing, shot on a locked tripod. Rich hand-woven Persian tribal carpets, embroidered floor cushions, glowing pierced Moroccan brass lanterns, and a circular stone hearth campfire overlooking golden sand dunes under the Milky Way galaxy. Strictly zero vehicles, zero plastic, zero tourists."
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

{motion_contract}

4. MODEL-SPECIFIC IMAGE PROMPTS ("image_model_configs") - MANDATORY NO FALLBACKS:
   - For every scene, generate model-tailored image prompts inside "image_model_configs" for ALL target image models ("flux_dev", "flux_pro", "zimage"):
     * "flux_dev": fal-ai/flux/dev, 16:9 cinematic framing, guidance_scale 3.5, 28 steps.
     * "flux_pro": fal-ai/flux-pro/v1.1-ultra, 8K UHD, 16:9, raw: true.
     * "zimage": fal-ai/z-image/turbo, sub-second high-detail photorealism, sharp natural lighting, 8 steps.

5. MODEL-SPECIFIC VIDEO DIFFUSION DIRECTIVES ("model_configs") - MANDATORY NO FALLBACKS:
   - For every scene, you MUST generate model-specific positive prompts, negative prompts, and optimal API settings inside "model_configs" for:
     * "kling_v3_4k": Model "fal-ai/kling-video/v3/4k/image-to-video". Cinemagraph living wallpaper, strictly locked stationary camera with zero movement, 100% frozen topography, fluid water and atmospheric dynamics with 4K UHD spatial depth. Settings: {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
     * "kling_v1_6_pro": Model "fal-ai/kling-video/v1.6/pro/image-to-video". Directorial action command style: "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs and horizon line remain 100% frozen and static. Continuous downward flowing water cascades directly matching the source image into the churning emerald basin, soft rising vapor mist, seamless cyclic motion, pristine untouched nature, zero humans." Settings: {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
     * "wan_2_1": Model "fal-ai/wan-i2v". Continuous fluid kinetic phrasing: "Living wallpaper cinemagraph. Strictly locked stationary camera on a heavy fixed tripod with zero camera movement, zero camera angles, zero pan, zero tilt, zero zoom, zero camera drift. Rock cliffs and landscape structure remain 100% frozen, solid, and unmoving. Smooth continuous laminar water cascades flowing steadily downwards into the basin, tranquil rising vapor mist. Stable uniform illumination, seamless loop compatible." Settings: {{ "guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9" }}
     * "local_drone": Model "local_perspective_drone". For relaxation format living wallpapers, camera movement MUST be strictly pure locked stationary frame: {{ "movement": "stay", "start_pan": "center", "start_zoom": "normal", "start_tilt": "center", "curve": "cosine", "speed_factor": 1.0, "rationale": "Pure locked stationary tripod living wallpaper framing with zero camera movement" }}.

8. DIRECTORIAL CAMERA RIG & MANDATORY NEGATIVE PROMPT (Rule 20):
   - Always provide "motion_negative_prompt" and model-specific negative prompts containing: "clouds, cloudy, overcast sky, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, camera flythrough, flickering, temporal jump, sunny sky, rainbow, changing lighting, sunlight shifts, altering colors, parched, frozen ice, stagnant water, motionless water, melting foam, rubbery water, artifacts, humans, tourist, boat, railings, buildings"

9. AUTONOMOUS LANDMARK DISCOVERY (WHEN NO PROMPT IS PROVIDED):
   - Use the supplied genre and archetype to choose a real, geographically accurate destination; do not substitute a generic or unrelated default location.
   - {landmark_research_directive}
   - Select one destination and derive a fresh title and story around its authentic landscape, while excluding previously produced topics listed above.
   - If the user supplied a prompt, treat it as the creative anchor and do not replace it with an unrelated destination.

10. BESPOKE SOOTHING RELAXATION AUDIO DIRECTIVE FOR SUNO (STRICT DIVERSITY):
   - Pure Relaxation Sound: Zero background song, zero vocals. Set vocal_gender: "none", singing_lyrics_spec: "".
   - Stochastic Instrument Diversity (Strict Ban on Hardcoded Repetition): NEVER hardcode or repeat the same instruments across productions. On every execution, Gemini MUST autonomously pick a fresh, unique blend of soothing instruments from diverse organic categories: Plucked (Celtic harp, koto, guzheng, classical nylon guitar, santur, sarod, kalimba, mbira, zither); Bowed (warm cello, gentle viola, erhu, acoustic bass drone); Winds (shakuhachi, bansuri bamboo flute, Native American cedar flute, pan flute, ocarina, wooden ney); Resonators & Bells (Tibetan singing bowls, crystal singing bowls, tuned handpan, wind chimes, celesta, vibraphone); Keys & Pads (felted upright piano, Rhodes, warm 432Hz/528Hz Solfeggio analog pads).
   - Direct Suno with Proper Soothing Instructions: Slow resting heartbeat tempo (48-54 BPM), 432Hz Solfeggio tuning, gentle note attacks with long smooth decays, zero harsh percussion, zero brass, zero vocals, pristine studio recording, zero background hiss.
{exclusion_block}
======================================================================
PRODUCTION SPECIFICATIONS:
======================================================================
- User Prompt / Concept Anchor: "{concept_anchor}"
- Genre: {genre}
- Total Duration: {duration_seconds} seconds
- Shot Count: {num_shots} shots ({per_shot_dur}s per shot)
- Camera Rig: {camera_motion}
- Target Image Models: ["flux_dev", "flux_pro", "zimage"] (ALL MANDATORY, ZERO FALLBACKS)
- Target Video Models: ["kling_v3_4k", "kling_v1_6_pro", "wan_2_1", "local_drone"] (ALL MANDATORY, ZERO FALLBACKS)

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
  "global_culture": {{ "continent_region": "Autonomously derive true region", "culture_heritage": "Authentic natural heritage", "authentic_textiles_and_fabrics": "Weathered stone, moss, slate, timber", "cultural_gestures_and_rituals": "Tranquil silence" }},
  "travel_tourism": {{ "destination_name": "True Landmark Name", "country": "Authentic Country", "province_state": null, "attraction_type": "True topographical structure", "best_season_and_lighting": "Optimal lighting" }},
  "cast": [],
  "audio_master": {{
    "audio_mode": "ambient_nature",
    "spoken_narration_script": "Authoritative, poetic voiceover sentence describing the timeless geological wonder and geographic lore.",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "432Hz Solfeggio, pure instrumental relaxation, <randomly selected lead instrument>, <accompaniment>, <texture>, peaceful soundscape, zero drums, zero vocals, -21 LUFS",
    "suno_prompt": "[Instrumental Ambient Meditation]\\n[Scene Context: <specific visual setting matching the image prompt>]\\n[Tempo: 50 BPM - Resting Heartbeat Pulse]\\n[Tuning: 432Hz Solfeggio Velvet Resonance]\\n[Lead Melody: Hypnotic, slow, tranquil phrasing on <Randomly Chosen Soothing Lead Instrument>]\\n[Accompaniment: Soft acoustic harmonies on <Randomly Chosen Second Instrument>]\\n[Atmosphere: <Randomly Chosen Resonator/Pad>, warm velvet ambient pads, long smooth reverb decays]\\n[Acoustic Direction: Studio master recording, zero harsh percussion, zero brass, zero vocals, zero hiss]\\n[Emotion: Deep tranquil peace, anxiety reduction, restorative sleep induction]\\n[Outro: Lingering resonant acoustic dissolve]",
    "vocal_gender": "none", "tempo_bpm": 50, "target_lufs": -21.0, "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1,
      "location_hub": "Specific Vista 1 Name matching actual topography",
      "shot_type": "wide_panoramic_picturesque",
      "camera_rig": "{camera_motion}",
      "color_temp_kelvin": 5500,
      "visual_prompt": "A photorealistic, wide panoramic landscape view of [Landmark Name]. Symmetrical 16:9 cinematic framing, shot on a locked tripod. In background, towering jagged mountain peaks; in foreground, lush alpine meadows with wildflowers frame a tranquil glacial stream. Pristine wilderness, zero buildings, zero tourists, zero modern structures.",
      "image_model_configs": {{
        "flux_dev": {{ "model": "fal-ai/flux/dev", "prompt": "Photorealistic wide panoramic view, 16:9 cinematic.", "aspect_ratio": "16:9", "guidance_scale": 3.5, "num_inference_steps": 28 }},
        "flux_pro": {{ "model": "fal-ai/flux-pro/v1.1-ultra", "prompt": "A photorealistic wide panoramic landscape of [Landmark Name], locked tripod, crisp natural daylight, pristine untouched wilderness.", "aspect_ratio": "16:9", "raw": true }},
        "zimage": {{ "model": "fal-ai/z-image/turbo", "prompt": "Stunning photorealistic panoramic landscape, 16:9 locked tripod framing, sharp natural lighting.", "aspect_ratio": "16:9", "num_inference_steps": 8 }}
      }},
      "motion_prompt": "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement, zero panning, zero tilting, zero zooming. Landscape structure remains 100% frozen and static. Continuous downward flowing stream water, soft slow-moving vapor mist, zero humans.",
      "motion_negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing environment, hallucinating objects, appearing foliage, shifting rocks, flickering, temporal jump, sunny sky, rainbow, changing lighting, artifacts, humans, tourist, boat, buildings",
      "model_configs": {{
        "kling_v3_4k": {{
          "model": "fal-ai/kling-video/v3/4k/image-to-video",
          "prompts": {{ "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Topography 100% frozen. Fluid motion, native 4K UHD atmospheric depth, zero humans.", "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing perspective, flickering, artifacts" }},
          "settings": {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
        }},
        "kling_v1_6_pro": {{
          "model": "fal-ai/kling-video/v1.6/pro/image-to-video",
          "prompts": {{ "positive_prompt": "Cinemagraph style, living wallpaper. Strictly locked stationary camera with zero movement. Rock cliffs remain 100% frozen and static. Continuous downward flowing water cascades, soft rising vapor mist, seamless cyclic motion, zero humans.", "negative_prompt": "camera movement, camera pan, panning, tilt, zoom, morphing landscape, changing perspective, flickering, artifacts" }},
          "settings": {{ "mode": "pro", "duration": "5", "aspect_ratio": "16:9" }}
        }},
        "wan_2_1": {{
          "model": "fal-ai/wan-i2v",
          "prompts": {{ "positive_prompt": "Living wallpaper cinemagraph. Strictly locked stationary camera on a heavy fixed tripod with zero camera movement, zero camera angles, zero pan, zero tilt, zero zoom, zero camera drift. Landscape structure remains 100% frozen, solid, and static. Smooth continuous laminar water cascades, tranquil rising vapor mist, seamless loop compatible.", "negative_prompt": "camera movement, camera motion, camera angles, camera pan, panning, tilt, zoom, dolly, drone, tracking shot, flythrough, handheld camera, camera drift, jitter, shaky camera, moving perspective, perspective shift, morphing landscape, changing perspective, flickering, artifacts" }},
          "settings": {{ "guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9" }}
        }},
        "local_drone": {{
          "model": "local_perspective_drone",
          "movement": "stay",
          "start_pan": "center",
          "start_zoom": "normal",
          "start_tilt": "center",
          "curve": "cosine",
          "speed_factor": 1.0,
          "rationale": "Pure locked stationary tripod living wallpaper framing with zero camera movement"
        }}
      }},
      "loop_strategy": {{ "target_clip_duration_seconds": {per_shot_dur}, "generation_segment_seconds": 5.0, "continuity_mode": "cyclic_temporal_flow", "seam_strategy": "forward_phase_aligned_crossfade", "unidirectional_flow": true, "crossfade_seconds": 1.2, "loop_validation": true }},
      "domain": "water_fluid",
      "motion_type": "{ex_motion_type}",
      "motion_engine": "{ex_motion_engine}",
      "narration_text": "Poetic, educational sentence narrating this specific vista or geological feature.",
      "camera_movement": {ex_camera_movement},
      "duration_seconds": {per_shot_dur}
    }}
  ],
  "publishing": {{
    "ctr_titles": ["3 HOURS of Deep Serenity in [Scene] ⋄ 432Hz Soundbath - 4K UHD", "Sleep Under [Scene] ✦ 432Hz Miracle Tone for Deep Rest - 4K", "[Scene] Living Wallpaper ⋄ 4K 60FPS Ambient Serenity"],
    "description_with_timestamps": "SEO YouTube description with timestamps...",
    "seo_tags": ["nature soundscape", "relaxing waterfall", "8k living wallpaper"],
    "has_synthetic_media": true,
    "ypp_monetization_safety": "100% AdSense Advertiser-Friendly (Green Dollar Guarantee)"
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only.
"""
