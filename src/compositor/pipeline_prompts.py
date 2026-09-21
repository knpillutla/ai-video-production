"""Storyboard prompt builder with support for custom scripts, themes, and ideas."""


def build_dance_storyboard_prompt(
    title: str,
    duration_seconds: int,
    language: str,
    genre: str = "romantic_dance",
    idea: str | None = None,
    art_style: str | None = None,
    lead_gender: str | None = None,
    character_name: str | None = None,
) -> str:
    """Build a Gemini Tier-2 prompt for broadcast dance video storyboards.

    Uses few-shot examples and strong cultural context injection so Gemini
    produces the same ultra-detailed prompts that a human director would write.
    """
    idea_line = f"\nPRIMARY CREATIVE DIRECTION (USER REQUEST — this is the most important input): {idea}" if idea else ""
    art_line = f"\nVisual Art Style: {art_style}." if art_style else ""
    char_line = f"\nLEAD CHARACTER SPECIFICATION: The lead character's name MUST be '{character_name}'. You must use '{character_name}' as the lead character in character metadata and across all scenes." if character_name else ""
    gender_line = (
        "\nCAST INFERENCE: Infer the lead cast from the user's creative direction and cultural context. "
        "Decide whether this is a male lead, female lead, or romantic production with both male and female co-leads. "
        "Return that decision explicitly in character metadata and every scene's gender fields."
    )
    return (
        f"You are a Gemini Tier-2 cinematic dance director, lyricist, and cultural expert. "
        f"Create a broadcast-grade {duration_seconds}-second {genre} dance video storyboard "
        f"in the {language} language/dialect."
        f"{idea_line}{art_line}{char_line}{gender_line}\n\n"
        "CRITICAL: The title, lyrics, wardrobe, locations, instruments, and ALL visual details "
        "MUST be authentically derived from the user's creative direction above. "
        "If the user says 'Telangana village atmosphere', every scene must be set in a Telangana village — "
        "NOT in neon clubs, wedding halls, urban nightclubs, or any setting that contradicts the user's intent. "
        "The title must directly reflect the user's requested theme and cultural setting.\n\n"
        "MANDATORY OUTPUT STRUCTURE (strict JSON):\n"
        "- 'title_en': Creative title in English (URL-safe, for file/folder naming)\n"
        "- 'title_localized': Creative title in the target language (for display/metadata)\n"
        "- 'titles_multilingual': Dict mapping language codes to creative titles for Batch Regional editions\n"
        "- 'hook_thesis': one-line thematic hook\n"
        "- 'recommended_fps': integer (24, 30, or 60) — use 30 for dance\n"
        "- 'vocal_gender': 'male', 'female', or 'duet' — based on the lead performer gender(s)\n"
        "- 'suno_tags': Suno music tags string e.g. '[folk genre], [BPM] BPM, [regional instruments], [vocal_gender] vocals'\n"
        "- 'lyrics': rhyming lyrical couplets in the target language/dialect with cultural meter and prasa (4–8 lines)\n"
        "- 'characters': list of character metadata objects\n"
        "- 'location_hubs': 3–4 distinct location hub names derived from the user's setting\n"
        "- 'scenes': list of 2–4 scene objects\n"
        "- Every scene MUST include 'lead_character_gender' and 'background_dancer_gender' fields.\n\n"
        "MANDATORY DANCE CHOREOGRAPHY & SHOT COMPOSITION DIRECTIVES:\n"
        "1. HIGH-ENERGY DANCE CHOREOGRAPHY FIRST: 70–80% of scenes MUST be dynamic wide_shot (full-body troupe formations, mid-air jumps, vigorous footwork, swirling skirts/lungis) or medium_shot (waist-up/three-quarter body with active arm mudras, rhythmic shoulder shrugs, and waist movements).\n"
        "2. ZERO STATIC CLOSE-UPS: Strictly prohibit tight static portrait headshots with no dance movement. Any close_up or medium_shot MUST be dynamic and feature active dancing—expressive rhythmic shoulder rolls, head tilts, and hand gestures in lockstep with the beat.\n"
        "3. RAW 35MM CINEMATIC FILM REALISM (ZERO PLASTIC / AI SHEEN): Prompts must depict raw, photorealistic 35mm film still photography (shot on Arri Alexa 35mm Master Prime lens, natural ambient daylight, visible skin micro-texture and pores, natural light perspiration, authentic South Asian skin tones, true handloom fabric texture). Strictly prohibit smooth airbrushed skin, CGI gloss, doll-like wax texture, or artificial yellow glow.\n"
        "4. CHARACTER CONSISTENCY: The lead character's name, facial structure, hairstyle, and exact wardrobe (shirt colors, lungi patterns, accessories) MUST remain 100% consistent across every single scene prompt.\n\n"
        "SCENE OBJECT FIELDS:\n"
        "- 'scene_index': integer starting at 0\n"
        "- 'duration_seconds': float (must sum to target duration)\n"
        "- 'location_hub': one of the location_hubs\n"
        "- 'shot_type': 'wide_shot', 'medium_shot', 'low_angle', or 'close_up'\n"
        "- 'choreography_phase': 'intro_groove', 'verse_acting', or 'beat_drop_hook'\n"
        "- 'choreography_steps': specific physical dance steps for this phase\n"
        "- 'visual_prompt': (SEE EXAMPLE BELOW — must be this level of detail)\n"
        "- 'motion_prompt': (SEE EXAMPLE BELOW — must be this level of detail)\n"
        "- 'dialogue': empty string (zero spoken TTS in dance videos)\n\n"
        "VISUAL PROMPT QUALITY STANDARD (every visual_prompt MUST match this level of detail):\n"
        "Each visual_prompt is the exact prompt sent to Fal FLUX.1-dev. It must be a self-contained, richly detailed cinematic image prompt matching raw 35mm film photography. It MUST explicitly contain: lead character name, age and gender; face, hair and body description; exact culturally appropriate wardrobe and accessories; background dancer gender and count; location and regional setting; visible props and instruments; dynamic choreography pose; shot type and lens/depth of field; time of day and lighting color; skin-tone/color fidelity; and negative constraints against plastic/CGI smoothness.\n"
        "EXAMPLE: 'Raw cinematic 35mm film still, South Indian Telugu man Arjun, 24 years old, balanced naturally fit lean-athletic build, handsome features, neatly groomed mustache, expressive eyes, wavy dark hair. Wearing a vibrant mustard-yellow floral block-printed half-sleeve cotton shirt over a maroon checkered handloom lungi folded high to the knees, red cotton thundu towel draped over shoulder. Full-body wide shot mid-leap during a high-energy teenmaar folk dance step, holding the lungi fold, kicking up golden dust clouds on an authentic rustic Telangana village dirt road. Eight male troupe dancers in colorful lungis dancing in synchronized background formation. Realistic natural skin texture with visible micro-pores, natural perspiration, true South Asian skin tones, 5400K open daylight, Arri Alexa 35mm Master Prime lens, zero plastic skin, zero CGI sheen, zero artificial yellow lens flare.'\n\n"
        "MOTION PROMPT QUALITY STANDARD:\n"
        "EXAMPLE: 'Raw cinematic 35mm film motion, 24-year-old South Indian male lead Arjun and eight male troupe dancers executing explosive high-tempo teenmaar folk choreography, simultaneous airborne jumps, heavy rhythmic foot-stomps kicking up golden dust clouds, synchronized arm pumps, fast tracking crane shot, flying lungi textiles and dynamic muscle movements, vibrant rustic village street backdrop, crisp natural 5400K sunlight, true-to-life human physics, 30fps.'\n\n"
        "CHARACTER METADATA FIELDS:\n"
        "- 'name': culturally authentic or matching requested character name\n"
        "- 'age': integer 23–27\n"
        "- 'gender': 'male' or 'female'\n"
        "- 'body_composition': 'medium_fit' (balanced fit build — never too skinny or chubby)\n"
        "- 'height': 'medium'\n"
        "- 'role': 'hero', 'heroine', 'supporting', or 'troupe'\n"
        "- 'relationship': 'lead', 'lover', 'friend', etc.\n"
        "- 'appearance_summary': rich visual description matching the cultural setting\n\n"
        "Respond ONLY with valid JSON. No markdown fences. No explanatory prose."
    )


def build_storyboard_prompt(
    title: str,
    duration_seconds: int,
    language: str,
    fmt_str: str,
    genre: str = "comedy",
    custom_script: str | None = None,
    idea: str | None = None,
    theme: str | None = None,
    refine_script: bool = False,
    art_style: str | None = None,
    architecture_style: str | None = None,
    camera_language: str | None = None,
) -> str:
    """Construct structured storyboard prompt for LLM or mock resolver."""
    fmt = fmt_str.lower()
    if custom_script:
        needs_refine = refine_script or any(k in custom_script.lower() for k in ("refine:", "polish:", "enhance:"))
        if needs_refine:
            base = (
                f"Refine, polish, and optimize this user screenplay into a broadcast-grade storyboard "
                f"for '{title}' with duration {duration_seconds}s in {language} language. "
                f"Enhance comedic timing and pacing while preserving the core premise.\n"
                f"Screenplay:\n{custom_script}"
            )
        else:
            base = (
                f"Execute this user-provided screenplay AS-IS without altering dialogue or adding unsolicited lines. "
                f"Structure the exact dialogue and actions into timed scenes totaling {duration_seconds}s in {language} language.\n"
                f"User Screenplay:\n{custom_script}"
            )
    elif idea:
        base = (
            f"Brainstorm and expand this creative story idea into a complete cinematic scene-by-scene script "
            f"for '{title}' with target duration {duration_seconds}s in {language} language.\n"
            f"Creative Idea & Angle: {idea}\n"
            f"Develop structured visual scenes, character beats, and natural dialogue paced perfectly for {duration_seconds} seconds."
        )
    elif any(k in fmt for k in ("dance",)):
        return build_dance_storyboard_prompt(
            title=title, duration_seconds=duration_seconds, language=language,
            genre=genre, idea=idea, art_style=art_style,
        )
    elif "travel_guide" in fmt or "guide" in fmt:
        base = (
            f"Write a captivating travel guide and city tour script on: {title}. "
            f"Feature top tourist attractions, historical landmarks, local culture, "
            f"and visitor tips with duration {duration_seconds}s in {language} language."
        )
    elif "vlog" in fmt:
        base = (
            f"Write an engaging, personal travel vlog script on: {title}. "
            f"Share authentic personal experiences, walking tours, and tips with "
            f"duration {duration_seconds}s in {language} language."
        )
    elif "movie" in fmt:
        base = (
            f"Write a dramatic, cinematic short film script on: {title} in {genre} "
            f"genre with duration {duration_seconds}s in {language} language."
        )
    elif any(k in fmt for k in ("relaxation", "scenic", "nature", "lounge", "walk", "drive")):
        base = (
            f"Write a serene, scenic visual relaxation script on: {title} in {fmt} "
            f"format. Emphasize breathtaking landscapes, ambient sound design, "
            f"peaceful pacing, and visual meditation with duration {duration_seconds}s in {language} language."
        )
    else:
        base = (
            f"Write an engaging, high-retention video script on: {title} in {genre} "
            f"genre with duration {duration_seconds}s in {language} language."
        )

    extras: list[str] = []
    if theme and theme.lower() != "auto":
        extras.append(f"Narrative Theme: {theme}.")
    if art_style:
        extras.append(f"Visual Art Style: {art_style}.")
    if architecture_style:
        extras.append(f"Architectural Style & Setting: {architecture_style}.")
    if camera_language:
        extras.append(f"Camera Cinematography: {camera_language}.")

    extras.append(
        "MANDATORY OUTPUT STRUCTURE (strict JSON):\n"
        "- 'title_en': Creative title in English (URL-safe, for file/folder naming)\n"
        "- 'title_localized': Creative title in the target language (for display/metadata)\n"
        "- 'titles_multilingual': Dict mapping language codes to creative titles for Batch Regional editions\n"
        "- 'hook_thesis': one-line thematic hook\n"
        "- 'recommended_fps': integer (24, 30, or 60)\n"
        "- 'vocal_gender': 'male', 'female', or 'duet'\n"
        "- 'characters': list of character metadata objects\n"
        "- 'scenes': list of scene objects\n"
    )
    extras.append(
        "MANDATORY CAST & WARDROBE DIRECTIVE: All main characters (male and female) must have a balanced, "
        "naturally fit medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves with toned midriff for women, "
        "lean-athletic fit build for men), strikingly beautiful / handsome in their mid-20s (ages 23-27). "
        "Autonomously derive setting aesthetics, background environment, and lighting directly from narrative context. "
        "Outfits and wardrobe MUST dynamically and authentically match the context of each scene in the story (e.g. festive village "
        "jathara -> vibrant traditional festive attire; modern IT office/WFH -> stylish smart-casual; rainy alpine trek -> "
        "functional stylish waterproof alpine outdoor wear; romantic evening -> elegant evening wear)."
    )
    extras.append(
        "MANDATORY DYNAMIC WEATHER & ENVIRONMENTAL KINETICS: In ALL genres (movies, music videos, rain dance, walking tours, documentaries), "
        "if rain, downpour, storm, monsoon, snow, blizzard, dust, or mist is present in the theme or scene, 'motion_prompt' MUST explicitly "
        "mandate visible dynamic weather physics: continuous sheets of heavy falling raindrops slicing through the frame, water droplets splashing "
        "off dancing bodies/faces, raindrops bouncing upward off wet ground with expanding ripples in puddles, swirling snowflakes, or dust plumes. "
        "Never output camera-only motion when dynamic weather is present."
    )

    if extras:
        base += " " + " ".join(extras)

    return base


def extract_dialogue_text(s: dict) -> str:
    """Extract clean string dialogue from string, dict, or list structures."""
    dlg = s.get("dialogue", "")
    if isinstance(dlg, dict):
        return str(dlg.get("text") or dlg.get("line") or dlg.get("content") or dlg.get("dialogue") or "")
    if isinstance(dlg, list):
        parts = []
        for item in dlg:
            if isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("line") or item.get("content") or item.get("dialogue") or ""))
            else:
                parts.append(str(item))
        return " ".join(parts)
    return str(dlg)
