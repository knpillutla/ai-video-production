"""Storyboard prompt builder with support for custom scripts, themes, and ideas."""


def build_dance_storyboard_prompt(
    title: str,
    duration_seconds: int,
    language: str,
    genre: str = "romantic_dance",
    idea: str | None = None,
    art_style: str | None = None,
) -> str:
    """Build a Gemini Tier-2 prompt for broadcast dance video storyboards.

    Uses few-shot examples and strong cultural context injection so Gemini
    produces the same ultra-detailed prompts that a human director would write.
    """
    idea_line = f"\nPRIMARY CREATIVE DIRECTION (USER REQUEST — this is the most important input): {idea}" if idea else ""
    art_line = f"\nVisual Art Style: {art_style}." if art_style else ""
    return (
        f"You are a Gemini Tier-2 cinematic dance director, lyricist, and cultural expert. "
        f"Create a broadcast-grade {duration_seconds}-second {genre} dance video storyboard "
        f"in the {language} language/dialect."
        f"{idea_line}{art_line}\n\n"
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
        "  MANDATORY: At least one scene MUST use 'close_up' or 'medium_shot' with the lead character's "
        "face clearly visible and prominent in frame (required for lip-sync face detection).\n\n"
        "SCENE OBJECT FIELDS:\n"
        "- 'scene_index': integer starting at 0\n"
        "- 'duration_seconds': float (must sum to target duration)\n"
        "- 'location_hub': one of the location_hubs\n"
        "- 'shot_type': 'wide_shot', 'medium_shot', 'close_up', or 'low_angle'\n"
        "- 'choreography_phase': 'intro_groove', 'verse_acting', or 'beat_drop_hook'\n"
        "- 'choreography_steps': specific physical dance steps for this phase\n"
        "- 'visual_prompt': (SEE EXAMPLE BELOW — must be this level of detail)\n"
        "- 'motion_prompt': (SEE EXAMPLE BELOW — must be this level of detail)\n"
        "- 'dialogue': empty string (zero spoken TTS in dance videos)\n\n"
        "VISUAL PROMPT QUALITY STANDARD (every visual_prompt MUST match this level of detail):\n"
        "EXAMPLE: 'Ultra-photorealistic 4K cinematic medium shot, 24-year-old South Indian Telugu woman, "
        "balanced naturally fit medium-slender build with graceful feminine curves, strikingly beautiful, "
        "big expressive almond eyes, gentle smiling dimples, thick dark wavy braid with fresh jasmine flowers. "
        "Wearing traditional Telangana festive silk half-saree (langa voni) in vibrant parrot green and magenta "
        "with golden zari border, silver payal anklets, colorful glass bangles, tiny bindi. "
        "Set in authentic Telangana village courtyard: earthen ground, lush green paddy fields and tamarind trees, "
        "rustic terracotta-roofed homes, colorful floral rangoli, mango-leaf toranalu overhead. "
        "Crisp balanced 5500K natural open-air daylight, soft morning sunlight, realistic natural skin tones, "
        "zero artificial yellow lens flare, 50mm f/2.0 cinematic lens, moderate depth-of-field.'\n\n"
        "MOTION PROMPT QUALITY STANDARD (every motion_prompt MUST match this level):\n"
        "EXAMPLE: 'Ultra-photorealistic 4K cinematic, 24-year-old South Indian woman with balanced naturally fit build "
        "performing graceful romantic folk dance, playful hip sway, delicate hand mudras, joyful teasing expressions, "
        "spinning half-turn with flared lehenga skirt, village courtyard with festive garlands swaying in breeze, "
        "fluid realistic human motion, crisp natural 5500K daylight, authentic skin tones, 30fps.'\n\n"
        "CHARACTER METADATA FIELDS:\n"
        "- 'name': culturally authentic to the language/region (e.g. Telugu: Swathi, Lakshmi, Raju, Venkat)\n"
        "- 'age': integer 23–27\n"
        "- 'gender': 'male' or 'female'\n"
        "- 'body_composition': 'medium_fit' (balanced fit build — never too skinny or chubby)\n"
        "- 'height': 'medium'\n"
        "- 'role': 'hero', 'heroine', 'supporting', or 'troupe'\n"
        "- 'relationship': 'lover', 'friend', 'lead', etc.\n"
        "- 'appearance_summary': rich visual description matching the cultural setting\n\n"
        "CULTURAL DERIVATION MANDATE:\n"
        "- Wardrobe, jewelry, hairstyles, instruments, locations MUST be authentically derived from the "
        "user's specified language, dialect, and setting — NOT generic Bollywood or Western.\n"
        "- If the user says 'Telangana village': use langa voni / Pochampally silk, gajjelu anklets, "
        "jasmine flowers, dappu drums, paddy fields, tamarind trees, terracotta homes.\n"
        "- If the user says 'Tamil temple': use Kanchipuram silk, temple jewelry, kolam, gopuram backdrop.\n"
        "- NEVER generate neon lights, nightclubs, urban wedding halls, or modern settings unless the user explicitly asks.\n\n"
        "LIGHTING: Natural 5400K–5600K daylight for outdoor; zero artificial yellow lens flares.\n"
        "PHYSICALITY: All leads balanced naturally fit build, strikingly beautiful/handsome, mid-20s.\n\n"
        "CHOREOGRAPHIC PROGRESSION (3-phase):\n"
        "  Phase 1 (intro_groove): swagger walk, shoulder shrugs, subtle hip sway, teasing abhinaya\n"
        "  Phase 2 (verse_acting): expressive hand mudras matching lyrics, half-turn spins\n"
        "  Phase 3 (beat_drop_hook): vigorous foot-stomping, rapid waist twists, spinning chakkars\n\n"
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
        "MANDATORY CHARACTER METADATA DIRECTIVE: In the 'characters' list, return structured metadata for every character: "
        "'name' (culturally authentic to the language and region, never hardcoded), 'age' (23-27), 'gender' ('male' or 'female'), "
        "'body_composition' ('skinny', 'medium_fit', 'athletic_strong', 'curvy_healthy', 'chubby'), 'height' ('short', 'medium', 'tall'), "
        "'role' ('hero', 'heroine', 'supporting', 'troupe'), 'relationship' ('lover', 'friend', 'mom', 'dad', 'son', 'daughter', 'lead'), "
        "and 'appearance_summary'. Set 'vocal_gender' ('male', 'female', or 'duet') based on lead singing performer(s)."
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
