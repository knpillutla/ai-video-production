"""Deterministic offline dance storyboard used only when live Gemini is unavailable."""


def resolve_mock_dance_storyboard(prompt: str) -> dict:
    """Return a contract-valid dance plan that preserves the requested regional context."""
    is_telugu = "telangana" in prompt.lower() or "language/dialect: te" in prompt.lower()
    title_en = "Telangana Village Dappu Dance" if is_telugu else "Regional Folk Dance Celebration"
    title_localized = "తెలంగాణ పల్లె డప్పు నృత్యం" if is_telugu else title_en
    setting = "Telangana village jathara courtyard" if is_telugu else "regional village festival courtyard"
    folk = "Telangana folk dappu and thappeta" if is_telugu else "regional folk percussion"
    lead = "South Indian Telugu lead dancer" if is_telugu else "folk dance lead performer"
    common = f"4K photorealistic {setting}, {lead}, healthy medium build, crisp 5500K natural daylight"
    return {
        "title_en": title_en,
        "title_localized": title_localized,
        "titles_multilingual": {"en": title_en, "te": title_localized} if is_telugu else {"en": title_en},
        "hook_thesis": f"A celebratory village folk performance powered by {folk} rhythms.",
        "recommended_fps": 30,
        "vocal_gender": "female",
        "suno_tags": f"{folk}, 132 BPM, female vocals",
        "lyrics": "[Hook]\nడప్పు మోగే పల్లె వేడుక, అడుగు అడుగున ఆనందం\n[Verse]\nచప్పట్లతో జాతర వెలుగు, నృత్యమే మన సంబరం",
        "characters": [{"name": "Lead", "age": 24, "gender": "female", "body_composition": "medium_fit"}],
        "location_hubs": [setting, "paddy-field festival edge", "banyan-tree performance circle"],
        "scenes": [
            {"scene_index": 0, "duration_seconds": 3.0, "location_hub": setting, "shot_type": "wide_shot", "choreography_phase": "intro_groove", "choreography_steps": "Swagger walk, shoulder shrugs, and dappu-timed hand claps.", "visual_prompt": f"{common}, wide troupe formation with dappu drummers and festival flags", "motion_prompt": "Measured swagger walk with shoulder shrugs and synchronized hand claps to the opening dappu rhythm.", "dialogue": ""},
            {"scene_index": 1, "duration_seconds": 3.0, "location_hub": "paddy-field festival edge", "shot_type": "medium_shot", "choreography_phase": "verse_acting", "choreography_steps": "Expressive hand mudras, half-turn spin, and troupe call-and-response.", "visual_prompt": f"{common}, medium shot with expressive folk hand mudras beside green paddy fields", "motion_prompt": "Expressive hand mudras and a half-turn spin as the troupe answers with rhythmic claps.", "dialogue": ""},
            {"scene_index": 2, "duration_seconds": 4.0, "location_hub": "banyan-tree performance circle", "shot_type": "low_angle", "choreography_phase": "beat_drop_hook", "choreography_steps": "Synchronized foot stomps, waist twists, troupe jumps, and a signature hook step.", "visual_prompt": f"{common}, low-angle explosive group hook step under a banyan tree", "motion_prompt": "High-energy synchronized foot stomps, waist twists, and troupe jumps on the beat drop.", "dialogue": ""},
        ],
    }


__all__ = ["resolve_mock_dance_storyboard"]
