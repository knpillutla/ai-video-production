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
__all__ = ["build_default_image_model_configs", "build_default_video_model_configs", "build_base_directorial_prompt"]


def build_base_directorial_prompt(
    genre: str, sub_genre: str, archetype: str, cluster: str,
    custom_prompt: Optional[str] = None, duration_seconds: float = 60.0,
    num_shots: int = 1, camera_motion: str = "locked_tripod",
    excluded_topics: Optional[List[str]] = None, specific_rules: str = "",
    curation_landmarks: Optional[List[str]] = None, color_temp_kelvin: int = 5500,
    channel_id: Optional[str] = None, tier: str = "balanced",
    extra_root_schema: str = "", extra_scene_schema: str = "",
    speech_cadence_wpm: int = 120, speech_words_per_sec: float = 2.0,
    tts_provider_name: str = "Azure Speech Neural", motion_model: Optional[str] = None,
    execution_mode: str = "prod",
) -> str:
    """Compose the authoritative directorial system prompt for Gemini storyboarding."""
    g_lower, a_lower = (genre or "").lower(), (archetype or "").lower()
    ch_lower, clean_tier = (channel_id or "").lower(), (tier or "balanced").strip().lower()
    m_lower = (motion_model or "").lower()
    is_prod_exec = (execution_mode or "prod").strip().lower() in ("prod", "production", "live")

    is_nature_relax = g_lower.startswith("relax") or "nature" in g_lower or a_lower in ("zen", "mountain", "forest", "ocean", "valley", "waterfall", "healing", "rain", "cozy", "blizzard", "hearth", "beach_lounge", "desert")
    is_urban_or_travel = g_lower.startswith("travel") or "travel" in g_lower or a_lower in ("cities", "tourist_places", "iconic_places", "spiritual_places", "natural_wonders", "remote_places") or ch_lower == "skylinediariesindia4k" or (ch_lower == "earth_serenade" and not is_nature_relax) or num_shots == -1
    is_documentary = "doc" in g_lower or "documentary" in ch_lower or "doc" in (sub_genre or "").lower() or "documentary" in a_lower
    tour_archetypes = {"itinerary_map_tour", "travel_itinerary_tour", "grand_tour", "top_attractions_tour", "local_neighborhood_tour", "culinary_food_tour", "architecture_design_tour"}
    is_tour = (a_lower in tour_archetypes) or ((sub_genre or "").lower().strip() in tour_archetypes)
    is_doc_format = is_documentary or cluster == "documentary" or is_tour or "doc" in g_lower or "nations" in g_lower
    is_auto_dur = (duration_seconds is None or duration_seconds <= 0 or duration_seconds == -1)
    user_chose_fixed_shots = (num_shots is not None and num_shots > 0 and num_shots != -1)
    if is_auto_dur:
        nom_dur = 180.0
        eff_shots = num_shots if user_chose_fixed_shots else (10 if is_doc_format else 8)
        per_shot_dur = round(nom_dur / max(1, eff_shots), 1)
        cadence_spec = f"- Target Duration: AUTO (-1) | Gemini authors the complete unabridged story for ALL syllabus chapters (~{nom_dur}s baseline)."
        schema_mandate = "\n- Author the FULL STORY for ALL chapters inside 'scenes' (or 'chapters'). Calculate duration dynamically from narration time."
    elif user_chose_fixed_shots:
        eff_shots = num_shots
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = f"- Target Duration: ~{duration_seconds}s | Explicit Shots: {eff_shots} (~{per_shot_dur}s/shot)"
        schema_mandate = f"\n- Generate exactly {eff_shots} scene(s) matching requested shot count inside 'scenes' with duration matching narration."
    elif is_tour:
        eff_shots = max(5, round(duration_seconds / 9.0))
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = f"- Target Duration: ~{duration_seconds}s | Tour Cadence: Landmark stops each with connecting route map."
        schema_mandate = "\n- Autonomously generate complete tour scenes matching the route and duration."
    else:
        eff_shots = max(2, round(duration_seconds / 12.0)) if (is_urban_or_travel or duration_seconds > 18.0) else max(1, round(duration_seconds / 6.0))
        per_shot_dur = round(duration_seconds / max(1, eff_shots), 1)
        cadence_spec = f"- Target Duration: ~{duration_seconds}s | Autonomous Cadence: {eff_shots} scenes (~{per_shot_dur}s each)."
        schema_mandate = f"\n- Generate {eff_shots} scenes inside 'scenes' with duration dynamically matched to narration."

    calc_dur = 180.0 if is_auto_dur else duration_seconds
    target_words = max(25, int(calc_dur * speech_words_per_sec))
    per_shot_words = max(8, int(per_shot_dur * speech_words_per_sec))
    eff_kelvin, tod_key, tod_desc = detect_lighting_directive(custom_prompt, archetype, color_temp_kelvin or 5500)
    lighting_block = format_universal_lighting_guardrails(tod_key, eff_kelvin, tod_desc)
    exclusion_block = ("\nPREVIOUSLY PRODUCED TOPICS (MANDATORY DEDUPLICATION):\n" + "\n".join(f"- {t}" for t in excluded_topics[-15:]) + "\n") if excluded_topics else ""
    landmarks_block = ("\nCURATED REGIONAL LANDMARK INSPIRATION:\n" + "\n".join(f"      {i}. {l}" for i, l in enumerate(curation_landmarks or [], 1)) + "\n") if curation_landmarks else ""
    channel_block = f"\n{profile.format_directorial_guardrails_block()}\n" if channel_id and (profile := get_channel_profile(channel_id)) else ""

    motion_rule = (
        f"3. HYBRID MOTION DIRECTORIAL CONTRACT (TIER: {clean_tier.upper()}):\n"
        '   - Gemini DECIDES "motion_type" ("ken_burns" | "ai_diffusion"), "recommended_model", and "motion_rationale" for every scene.\n'
        '   - Default for purely static architecture, interiors & solid geometry: "ken_burns" ($0.00 compute local 4K perspective engine).\n'
        '   - MOVABLE OBJECTS MANDATE (AI DIFFUSION): Whenever a scene features any movable or dynamic objects—including water, rivers, canals, lakes, ocean waves, waterfalls, clouds, skies, smoke, fire, humans, pedestrians, crowds, artisans, vehicles (cars, buses, trucks, trains), boats, ships, birds, or airplanes—Gemini MUST specify "motion_type": "ai_diffusion" so those elements move organically and never look static!\n'
        '   - PROD MODE HUMAN MOTION MANDATE (KLING): In PROD mode, if an image/scene features humans (pedestrians, crowds, artisans, dancers, locals, performers, people), Gemini MUST specify "recommended_model": "kling_v3_4k" (or "kling_pro") with "motion_type": "ai_diffusion". Kling is required for authentic human anatomy and fluid locomotion without distortion.\n'
        '   - When "motion_type" is "ai_diffusion", Gemini MUST specify "recommended_model":\n'
        '     * "kling_v3" / "kling_v3_4k": Mandatory for humans in prod mode; violent water impact, plunging waterfalls, roaring cataracts, crashing ocean surf, fire/embers.\n'
        '     * "kling_pro": Complex human/animal movement, street vehicles, and cinemagraph living wallpapers.\n'
        '     * "h3_max": MiniMax H3 Max Turbo (~$0.015/sec) for subtle atmospheric micro-motion without humans (moving clouds, smoke plumes, light water surface ripples, gentle foliage rustle; topography 100% structurally frozen).\n'
        '     * "wan_2_1" / "wan_4k": Smooth laminar fluids, glassy rivers, gentle rain, lake reflections, drifting mist/smoke.\n'
        '     * "local_drone": Static topography, architectural monuments, and mountain flights ($0.00 compute).\n'
        '   - SEQUENTIAL & PARALLEL MOVEMENTS: Direct timeline arrays (e.g. [{"movement": "dollyin", "duration": 6.0}]) or compound movements.'
    )

    is_low = clean_tier in ("low_cost", "tier_0", "local")
    is_balanced = clean_tier in ("balanced", "standard", "default", "normal")
    diff_model = "kling_v3" if ("kling" in m_lower or is_prod_exec) else ("wan_4k" if "4k" in m_lower else "wan_2_1")

    if is_nature_relax:
        d1 = ("1. PURE PRISTINE LIVING WALLPAPER SCENERY & NATURAL GRANDEUR:\n"
              "   - Every scene MUST showcase exceptionally visually brilliant, pristine, awe-inspiring natural scenery.\n"
              "   - Strictly zero clutter, tourists, power lines, or modern vehicles. Living wallpaper overlooking scenic expanse.")
        if is_low:
            ex_motion_type, ex_rec_model = "ken_burns", "local_drone"
            ex_rationale = "Fixed locked tripod overlooking natural scenery via local 4K steady hold ($0.00 compute)."
            motion_rule = ("3. TIER-0 / LOW-COST LOCKED TRIPOD KEN BURNS DIRECTORIAL CONTRACT ($0.00 COMPUTE):\n"
                           '   - MANDATORY "motion_type": "ken_burns", "camera_movement": ["stay"], "recommended_model": "local_drone".')
        elif is_balanced:
            ex_motion_type, ex_rec_model = "ken_burns", "local_drone"
            ex_rationale = "100% local 4K steady hold on still nature scenery with zero moving elements ($0.00 compute)."
            motion_rule = (
                "3. BALANCED TIER DIRECTORIAL CONTRACT (80% LOCAL DRONE / 20% AI DIFFUSION COST SPLIT):\n"
                '   - MANDATORY 80/20 COST-OPTIMIZATION SPLIT ACROSS SCENES:\n'
                '     * 80% OF SCENES MUST USE "motion_type": "ken_burns", "recommended_model": "local_drone", camera_movement: ["stay"]. Zero moving elements!\n'
                f'     * 20% OF SCENES MUST USE "motion_type": "ai_diffusion", "recommended_model": "{diff_model}". Reserved for dynamic hero water/foliage motion.'
            )
        else:
            ex_motion_type, ex_rec_model = "ai_diffusion", diff_model
            ex_rationale = "Living wallpaper cinemagraph via AI video diffusion animating natural water and foliage kinematics."
            motion_rule = (f"3. HYBRID AI DIFFUSION LIVING WALLPAPER CONTRACT (TIER: {clean_tier.upper()}):\n"
                           '   - MANDATORY "motion_type": "ai_diffusion", "camera_movement": "locked_stationary_cinemagraph", "camera_rig": "locked_tripod_telephoto".')
        rig_palette, default_rig, default_cam_move = '["locked_tripod_telephoto"]', "locked_tripod_telephoto", "locked_stationary_cinemagraph"
        cam_contract = (
            "4. FIXED LOCKED TRIPOD (RELAXATION MANDATE - ZERO CAMERA MOVEMENT):\n"
            "   - Camera is 100% FIXED LOCKED TRIPOD. Zero camera angles, pans, tilts, zooms, or sweeps.\n"
            "   - 'camera_rig': 'locked_tripod_telephoto'. 'camera_movement': 'locked_stationary_cinemagraph' (or ['stay']). Topography 100% frozen."
        )
    else:
        d1 = ("1. 4K CINEMATIC BLUE-CHIP DOCUMENTARY & CAMERA MOTION:\n"
              "   - Story-Driven Visual Brilliance: Curate distinct landmarks, energy grids, factories, universities, and landscapes matching narration.\n"
              "   - Dynamic Ken Burns Camera Flights: Run local perspective camera movements (dolly, pan, tilt) so documentaries NEVER feel static.\n"
              "   - Authoritative Measured Narration (~120 WPM). 100% Crisp Natural Lighting.")
        diff_doc_model = "kling_v3" if (is_doc_format and is_prod_exec) else ("h3_max" if is_doc_format else ("kling_v3" if "kling" in m_lower else ("wan_4k" if "4k" in m_lower else "kling_pro")))
        if is_low:
            ex_motion_type, ex_rec_model = "ken_burns", "local_drone"
            ex_rationale = "100% local 4K perspective drone flight via ken_burns compound choreography ($0.00 compute)."
        elif is_balanced:
            ex_motion_type, ex_rec_model = "ken_burns", "local_drone"
            ex_rationale = "100% local 4K perspective drone flight with camera movement over scene subject ($0.00 compute)."
            motion_rule = (
                "3. BALANCED TIER DIRECTORIAL CONTRACT (GEMINI AUTONOMOUS MOTION DECISION):\n"
                '   - MANDATORY 80/20 COST-OPTIMIZATION SPLIT ACROSS SCENES:\n'
                '     * STATIC ARCHITECTURE, INTERIORS & SOLID LANDSCAPES -> Choose "motion_type": "ken_burns", "recommended_model": "local_drone".\n'
                '       DYNAMIC LOCAL CAMERA FLIGHT ($0.00 COMPUTE): These are NOT static screens! The local perspective engine executes dynamic camera motion ("dollyin", "dollyout", "pan-right", "pan-left", "tilt-up") across stunning 4K images illustrating that scene\'s topic.\n'
                f'     * SHOTS WITH ANY MOVABLE / DYNAMIC OBJECTS -> Choose "motion_type": "ai_diffusion", "recommended_model": "{diff_doc_model}".\n'
                '       Whenever a shot contains any movable or dynamic objects—including humans, pedestrians, crowds, artisans, vehicles (cars, buses, trucks, trains), boats, ships, birds, airplanes, water (rivers, canals, lakes, ocean waves, waterfalls), clouds, skies, smoke, or fire—Gemini MUST set "motion_type": "ai_diffusion", "recommended_model": "h3_max" (or "kling_v3_4k" in prod mode), and "duration_seconds": 5.0 (STRICTLY 5.0s for cost saving; NEVER expand a 5s AI diffusion clip because movable objects would freeze!). Author additional complementary "local_drone" shots ($0.00) of static architectural/landscape angles to cover the rest of the chapter duration!'
            )
        else:
            ex_motion_type, ex_rec_model = "ai_diffusion", diff_doc_model
            ex_rationale = "Cinematic drone perspective flight via AI video diffusion."
        rig_palette = '["heavy_lift_cine_drone", "technocrane_jib", "stabilized_steadicam_gimbal", "motorized_cine_slider"]'
        default_rig = "heavy_lift_cine_drone"
        default_cam_move = "stay" if is_nature_relax else "dollyin"
        cam_contract = (
            "4. CAMERA RIG & MOTION DIRECTORIAL CONTRACT:\n"
            "   - For AI diffusion models (kling, wan), camera motion is directed in natural language in their prompts.\n"
            "   - For local drone ('model_configs.local_drone'), motion MUST use supported engine movements: 'stay', 'dollyin', 'dollyout', 'slow-drone-forward', 'slow-drone-pullback', 'crane-ascend', 'crane-descent', 'drone-sweep-left', 'drone-sweep-right', 'pan-left', 'pan-right', 'tilt-up', 'tilt-down', 'orbit-left', 'orbit-right', 'drift-up-right', 'drift-up-left', 'drift-down-right', 'drift-down-left', 'roll-left', 'roll-right', 'level', or multi-stage 'movements' arrays.\n"
            "   - Root 'camera_movement' MUST mirror the primary movement string ('stay', 'dollyin', 'pan-right', etc.)."
        )

    is_flight = is_doc_format or is_urban_or_travel or is_tour
    ex_zimg = "Hyper-realistic 4K UHD panoramic aerial drone vista shot on Hasselblad H6D-100c with 18mm lens. Sweeping 45-degree bird's-eye view, vibrant emerald green hills, sun-drenched golden terracotta rooftops, radiant amber sunset sidelight, deep cobalt sky, crystalline clarity, rich natural color saturation, razor-sharp textures, 16:9." if is_flight else "Hyper-realistic 4K UHD cinematic landscape shot on Hasselblad H6D-100c, locked tripod. Radiant golden sunlight streaming across vibrant emerald moss, glistening crystal reflections, rich amber bark textures, saturated natural jewel tones, deep dynamic range, razor-sharp detail, 16:9."
    ex_mot = "Cinematic 4K drone flight. Sweeping slow forward glide and gentle 3D orbital banking arc around the landmark with majestic parallax." if is_flight else "Living wallpaper cinemagraph style. Strictly locked stationary camera on a heavy fixed tripod with zero camera movement, zero pan, zero tilt, zero zoom. Entire frame 100% frozen."
    ex_mot_neg = "camera shake, jitter, rapid jerky movements, erratic flight, morphing architecture, flickering, distortion, artifacts, humans" if is_flight else "camera movement, camera motion, camera angles, camera pan, panning, camera tilt, camera zoom, rotation, dolly, drone, tracking shot, flythrough, jitter, artifacts, humans"
    ex_kl_pos = "Cinematic 4K heavy-lift drone flight, smooth forward glide with subtle 3D orbital parallax. Monumental scale, deep atmospheric clarity, zero humans." if is_flight else "Cinemagraph style, living wallpaper. Strictly locked stationary camera on a fixed tripod with zero camera movement, zero camera angles. Topography 100% frozen, zero humans."
    ex_kl_neg = "camera shake, jitter, jerky motion, rapid speed changes, erratic maneuvers, morphing structures, artifacts" if is_flight else "camera movement, camera motion, camera angles, camera pan, camera tilt, camera zoom, rotation, dolly, drone, tracking shot, flythrough, jitter, artifacts"
    ex_wan_pos = "Cinematic slow aerial glide, smooth forward camera movement with natural atmospheric depth. Fluid environmental motion, seamless flight." if is_flight else "Living wallpaper cinemagraph. Strictly locked stationary camera on a heavy fixed tripod with zero camera movement. Topography 100% frozen. Smooth laminar fluid dynamics."

    root_ext = f"{extra_root_schema.strip()}\n" if extra_root_schema and extra_root_schema.strip() else ""
    scene_ext = f"{extra_scene_schema.strip()}\n" if extra_scene_schema and extra_scene_schema.strip() else ""

    dur_label = "AUTO (-1) - Full story duration derived from narration word count" if is_auto_dur else f"~{duration_seconds}s"
    return f"""You are the Master Visual Director and Senior Cinematic Storyboard Artist for CineAI Studio.
Your absolute #1 mandate is to author an exceptionally visually brilliant, breathtaking, stunning visual production. Every scene must be designed to wow the viewer with awe-inspiring beauty, immaculate environmental composition, rich cinematic depth, and pristine optical fidelity.
Your role is to author a complete, production-ready, broadcast-grade Screenplay for the "{genre}" channel genre.

{channel_block}
{lighting_block}

======================================================================
UNIVERSAL CINEMATIC DIRECTIVES (MANDATORY FOR ALL SCENES):
======================================================================
{d1}

2. EXCEPTIONAL, VISUALLY BRILLIANT & STUNNING CINEMATIC COMPOSITION:
   - Every "visual_prompt" MUST craft an exceptionally visually brilliant, colorful, bright, rich, and elegant scene.
   - MANDATORY RICH COLOR & HYPER-REALISTIC OPTICS: Name vivid palette colors (luminous turquoise, emerald greens, golden amber, deep cobalt). Specify hyper-realistic 4K UHD Hasselblad/Leica prime optics with high dynamic range, warm golden sidelight, and razor-sharp textures. Never produce desaturated or grey-hazy visuals.
   - Format visual and motion framing as a LIVING WALLPAPER / CINEMAGRAPH with wide panoramic grandeur.
   - In "shot_type", use cinematic panoramic classifications: "wide_panoramic_picturesque", "aerial_grandeur_vista", "low_angle_monumental", or "architectural_perspective_50mm".

{motion_rule}

{cam_contract}

5. DIRECTORIAL SCENE CADENCE & DURATION BUFFER (+LEEWAY):
   - Target Total Duration: {dur_label} (Directorial Leeway Buffer of +15% to +25%, or up to +60s for tours is explicitly permitted).
   - Allocate duration based on shot grandeur: 4s-6s (detail/establishing), 8s-12s (orbit/lateral glide), 14s-20s (monumental hold / transit maps).
   - DIRECTORIAL RULE: If a scene requires more narrative context or transit explanation, Gemini MUST INCREASE 'duration_seconds' to match: required_duration = (word_count / {speech_words_per_sec:.2f}) + 1.5s pause. Never truncate narration or rush speech!

6. MULTI-MODEL PROMPTS ("image_model_configs" & "model_configs") - MANDATORY NO FALLBACKS:
   - For every scene, populate ALL target image models in "image_model_configs":
     * "flux_dev": Hyper-realistic 16:9 cinematic framing (guidance_scale 3.5, 28 steps), Leica/Zeiss prime lens, saturated natural colors, warm golden sidelight, razor-sharp textures, deep dynamic range.
     * "flux_pro": Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c prime lens, 16:9, raw: true, rich natural jewel tones, golden amber sidelight, deep architectural and environmental relief.
     * "zimage": Hyper-realistic 4K UHD via fal-ai/z-image/turbo (8 steps). MANDATORY RICHNESS: Must specify Hasselblad/Leica prime lens, vivid specific colors (emerald green, cobalt blue, golden amber, terracotta), warm golden sidelight, crystalline clarity, razor-sharp textures, rich natural contrast (never flat or sterile).
   - For every scene, populate ALL target video models in "model_configs":
     * "h3_max": MiniMax H3 Max Turbo (fal-ai/minimax/h3-max-turbo/image-to-video) ~$0.015/sec. Subtle atmospheric movement. Low-intensity micro-motion: moving clouds, smoke plumes, light water ripples, gentle foliage breeze. Architecture & topography 100% frozen, mode: "turbo", duration: "5", aspect_ratio: "16:9".
     * "kling_v3_4k": Native 4K UHD video diffusion (fal-ai/kling-video/v3/4k/image-to-video), mode: "pro", duration: "5", aspect_ratio: "16:9".
     * "kling_v1_6_pro": Cinemagraph living wallpaper (fal-ai/kling-video/v1.6/pro/image-to-video), mode: "pro", duration: "5", aspect_ratio: "16:9".
     * "wan_2_1": Continuous laminar fluid dynamics (fal-ai/wan-i2v), guide_scale 5.0, 30 steps.
     * "local_drone": Camera flight capabilities ("movement": "dollyin"|"dollyout"|"slow-drone-forward"|"slow-drone-pullback"|"crane-ascend"|"crane-descent"|"drone-sweep-left"|"drone-sweep-right"|"pan-left"|"pan-right"|"tilt-up"|"tilt-down"|"orbit-left"|"orbit-right"|"drift-up-right"|"drift-up-left"|"drift-down-right"|"drift-down-left"|"roll-left"|"roll-right"|"level", or multi-stage "movements" arrays; "stay" for relax).

7. MANDATORY NEGATIVE PROMPT:
   - For Rain/Storms: "sunny, bright sun, direct sunlight, clear blue sky, lens flare, sunbeams, golden hour flare, camera shake, jitter, rapid motion, morphing architecture, gelatinous water, artifacts, humans, tourist".
   - For Fair-Weather Nature: "moving clouds, timelapse clouds, camera shake, jitter, rapid motion, morphing architecture, changing furniture, structural drift, flickering, temporal jump, gelatinous water, artifacts, humans, tourist".

8. NARRATION ENGINE & AUDIO-VISUAL GROUNDING CONTRACT (MANDATORY):
   - Active Narration Engine: {tts_provider_name} ({speech_cadence_wpm} WPM, ~{speech_words_per_sec:.2f} words/sec). Tail breathing pause: 1.5s.
   - Per-Scene Word Formula: Max words = (duration_seconds - 1.5s) * {speech_words_per_sec:.2f}. Total script ~{target_words} words.
   - Divide narration smoothly across 'scenes[].narration_text' perfectly matching each shot's 'duration_seconds'.
   - MANDATORY AUDIO-VISUAL GROUNDING (SHOW-AND-TELL RULE): Every scene's 'narration_text' MUST DIRECTLY DESCRIBE AND INTERPRET WHAT IS VISIBLE ON SCREEN in that scene's 'visual_prompt'. Strictly prohibit phantom subjects (e.g., describing rivers when viewing desert reservoirs, or narrating handheld artifacts in wide drone vistas).
    - Continuous Camera Motion: Visual camera motion runs for the FULL duration of the scene, ensuring continuous flight while narration speaks with ZERO frozen frames.
    - "suno_musical_tags" & "suno_prompt": For relaxation, Gemini MUST generate relaxing music directions to Suno that directly suit and complement the exact visual image and scene being created (beach, luxury terrace, desert, Swiss Alps, forest, cozy hearth). Both 'audio_master.suno_prompt' AND 'audio_master.suno_musical_tags' must be populated with scene-matched soothing instruments, 432Hz tuning, resting 48-54 BPM tempo, long decays, zero percussion, zero drums, zero vocals, -21 LUFS. Never leave suno_prompt empty!

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
- Target Image Models: ["flux_dev", "flux_pro", "zimage"] (ALL MANDATORY, ZERO FALLBACKS)
- Target Video Models: ["kling_v3_4k", "kling_v1_6_pro", "wan_2_1", "h3_max", "local_drone"] (ALL MANDATORY, ZERO FALLBACKS)

CRITICAL SCHEMA ENFORCEMENT:
Return ONLY a valid JSON object matching RelaxScreenplay:{schema_mandate}
{{
  "production_id": "EP-001",
  "title": "Authentic Atmospheric Title for the specific location",
  "story_topic": "Detailed sensory synopsis tailored to the true geography",
  "genre": "{genre}",
  "sub_genre": "{sub_genre}",
  "primary_archetype": "{archetype}", "secondary_archetype": null, "cluster": "{cluster}", "tier": "{clean_tier}",
  "primary_language": "en", "target_dubbing_languages": ["en", "de", "fr", "ja", "es"], "recommended_fps": 24, "aspect_ratio": "16:9", "total_duration_seconds": {calc_dur},
{root_ext}  "global_culture": {{ "continent_region": "Autonomously derive true region", "culture_heritage": "Authentic regional natural heritage", "authentic_textiles_and_fabrics": "Weathered stone, moss, river slate, native timber", "cultural_gestures_and_rituals": "Mindful silence" }},
  "travel_tourism": {{ "destination_name": "True Landmark Name", "country": "Authentic Country", "province_state": null, "attraction_type": "Autonomously derive true structure", "best_season_and_lighting": "Optimal season and lighting" }},
  "cast": [],
  "audio_master": {{
    "audio_mode": "ambient_nature",
    "spoken_narration_script": "Continuous unbroken master voiceover (~{target_words} words for {dur_label} at {speech_cadence_wpm} WPM), seamlessly narrating the journey without loops.",
    "singing_lyrics_spec": "",
    "suno_musical_tags": "432Hz Solfeggio, pure instrumental relaxation, warm velvet pads, 52 BPM, zero vocals, zero drums, -21 LUFS",
    "suno_prompt": "[Instrumental Ambient Meditation]\\n[Tempo: 50 BPM]\\n[Tuning: 432Hz]\\n[Emotion: Deep tranquil calm]",
    "vocal_gender": "none", "tempo_bpm": 80, "speech_cadence_wpm": 125, "target_lufs": -14.0, "ducking_db": -18.0
  }},
  "scenes": [
    {{
      "scene_index": 1, "location_hub": "Specific Vista 1 Name", "shot_type": "wide_panoramic_picturesque", "camera_rig": "{default_rig}", "color_temp_kelvin": {eff_kelvin},
      "visual_prompt": "A photorealistic, symmetrical 16:9 cinematic landscape view of [Landmark Name], shot from {default_rig}. Crisp natural lighting.",
{scene_ext}      "image_model_configs": {{
        "flux_dev": {{"model": "fal-ai/flux/dev", "prompt": "Hyper-realistic 4K UHD landscape, 16:9 cinematic framing, vibrant saturated natural colors, warm golden amber sidelight, razor-sharp textures, crystalline atmospheric depth.", "aspect_ratio": "16:9", "guidance_scale": 3.5, "num_inference_steps": 28}},
        "flux_pro": {{"model": "fal-ai/flux-pro/v1.1-ultra", "prompt": "Ultra-photorealistic 8K UHD shot on Hasselblad H6D-100c prime lens, 16:9 panoramic, rich saturated jewel tones, golden amber sidelight, deep dynamic range, razor-sharp micro-textures.", "aspect_ratio": "16:9", "raw": true}},
        "zimage": {{"model": "fal-ai/z-image/turbo", "prompt": "{ex_zimg}", "aspect_ratio": "16:9", "num_inference_steps": 8}}
      }},
      "motion_prompt": "{ex_mot}",
      "motion_negative_prompt": "{ex_mot_neg}",
      "model_configs": {{
        "h3_max": {{"model": "fal-ai/minimax/h3-max-turbo/image-to-video", "prompts": {{"positive_prompt": "Subtle atmospheric movement, locked stationary camera on heavy fixed tripod. Landscape and architecture 100% structurally frozen. Subtle organic drifting clouds and water ripples.", "negative_prompt": "camera movement, camera pan, tilt, zoom, camera shake, jitter, rapid motion, morphing architecture, changing scenery, distortion, artifacts"}}, "settings": {{"mode": "turbo", "duration": "5", "aspect_ratio": "16:9"}}}},
        "kling_v3_4k": {{"model": "fal-ai/kling-video/v3/4k/image-to-video", "prompts": {{"positive_prompt": "{ex_kl_pos}", "negative_prompt": "{ex_kl_neg}"}}, "settings": {{"mode": "pro", "duration": "5", "aspect_ratio": "16:9"}}}},
        "kling_v1_6_pro": {{"model": "fal-ai/kling-video/v1.6/pro/image-to-video", "prompts": {{"positive_prompt": "{ex_kl_pos}", "negative_prompt": "{ex_kl_neg}"}}, "settings": {{"mode": "pro", "duration": "5", "aspect_ratio": "16:9"}}}},
        "wan_2_1": {{"model": "fal-ai/wan-i2v", "prompts": {{"positive_prompt": "{ex_wan_pos}", "negative_prompt": "{ex_kl_neg}"}}, "settings": {{"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"}}}},
        "local_drone": {{"model": "local_perspective_drone", "movement": "{'stay' if is_nature_relax else 'dollyin'}", "start_pan": "center", "start_zoom": "normal", "curve": "cosine", "rationale": "{ex_rationale}"}}
      }},
      "domain": "landscape_solid", "motion_type": "{ex_motion_type}", "recommended_model": "{ex_rec_model}", "camera_movement": "{default_cam_move}",
      "kinetic_micro_zones": {{ "sprites": [], "tree_sway_zones": [], "water_zones": [] }}, "motion_rationale": "{ex_rationale}", "duration_seconds": {per_shot_dur},
      "narration_text": "Evocative, continuous narration for this vista (~{per_shot_words} words) paced smoothly for {per_shot_dur}s."
    }}
  ],
  "publishing": {{
    "ctr_titles": ["3 HOURS of Deep Serenity in [Landmark] ⋄ 432Hz Soundbath - 4K UHD", "Sleep Under [Landmark Sky] ✦ 432Hz Tone - 4K"],
    "description_with_timestamps": "Immerse yourself in [Landmark Name]. Broadcast 4K clarity.\\n\\n⏱️ Chapters:\\n0:00 - Vista 1",
    "seo_tags": ["nature relaxation", "living wallpaper", "4k nature", "ambient nature"],
    "has_synthetic_media": true, "ypp_monetization_safety": "100% Green Dollar Guarantee", "thumbnail_concept_prompts": ["Ultra-crisp 16:9 cinematic shot of [Landmark Name], striking natural lighting."]
  }}
}}
Do NOT output markdown backticks or preamble. Output raw JSON only."""
