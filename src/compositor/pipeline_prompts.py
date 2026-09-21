"""Storyboard prompt builder with support for custom scripts, themes, and ideas."""


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

    # Mandatory Workspace Directives: Physicality & Autonomous Contextual Outfits
    extras.append(
        "MANDATORY CAST & WARDROBE DIRECTIVE: All main characters (male and female) must have a balanced, "
        "naturally fit medium-slender build (neither too skinny/bony nor too chubby, graceful feminine curves with toned midriff for women, "
        "lean-athletic fit build for men), strikingly beautiful / handsome in their mid-20s (ages 23-27). "
        "Autonomously derive setting aesthetics, background environment, and lighting directly from narrative context. "
        "Outfits and wardrobe MUST dynamically and authentically match the context of each scene in the story (e.g. festive village "
        "jathara -> vibrant traditional festive attire; modern IT office/WFH -> stylish smart-casual; rainy alpine trek -> "
        "functional stylish waterproof alpine outdoor wear; romantic evening -> elegant evening wear)."
    )

    if extras:
        base += " " + " ".join(extras)

    return base
