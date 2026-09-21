"""Gemini-compatible JSON schema for dance video storyboard structured output.

Provides the schema that Gemini uses to produce structured JSON responses.
No Pydantic validation models — quality is enforced through prompt engineering
and examples, not rigid field constraints.
"""


def gemini_dance_schema() -> dict:
    """Return a compact Gemini-compatible JSON schema without Pydantic refs."""
    gender_values = {"type": "STRING"}
    lead_scene_values = {"type": "STRING"}
    scene = {
        "type": "OBJECT",
        "properties": {
            "scene_index": {"type": "INTEGER"},
            "duration_seconds": {"type": "NUMBER"},
            "location_hub": {"type": "STRING"},
            "shot_type": {"type": "STRING", "enum": ["wide_shot", "medium_shot", "close_up", "low_angle"]},
            "choreography_phase": {"type": "STRING", "enum": ["intro_groove", "verse_acting", "beat_drop_hook"]},
            "choreography_steps": {"type": "STRING"},
            "lead_character_gender": lead_scene_values,
            "background_dancer_gender": {"type": "STRING"},
            "visual_prompt": {"type": "STRING"},
            "motion_prompt": {"type": "STRING"},
            "dialogue": {"type": "STRING"},
        },
        "required": [
            "scene_index", "duration_seconds", "location_hub", "shot_type",
            "choreography_phase", "choreography_steps", "lead_character_gender",
            "background_dancer_gender", "visual_prompt", "motion_prompt", "dialogue",
        ],
    }
    character = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"}, "age": {"type": "INTEGER"},
            "gender": gender_values,
            "body_composition": {"type": "STRING"}, "height": {"type": "STRING"},
            "role": {"type": "STRING"}, "relationship": {"type": "STRING"},
            "appearance_summary": {"type": "STRING"},
        },
        "required": ["name", "age", "gender", "body_composition", "height", "role", "relationship", "appearance_summary"],
    }
    return {
        "type": "OBJECT",
        "properties": {
            "title_en": {"type": "STRING"}, "title_localized": {"type": "STRING"},
            "titles_multilingual": {"type": "OBJECT"}, "hook_thesis": {"type": "STRING"},
            "recommended_fps": {"type": "INTEGER"},
            "vocal_gender": {"type": "STRING"},
            "suno_tags": {"type": "STRING"}, "lyrics": {"type": "STRING"},
            "characters": {"type": "ARRAY", "items": character},
            "location_hubs": {"type": "ARRAY", "items": {"type": "STRING"}},
            "scenes": {"type": "ARRAY", "items": scene},
        },
        "required": [
            "title_en", "title_localized", "titles_multilingual", "hook_thesis",
            "recommended_fps", "vocal_gender", "suno_tags", "lyrics", "characters",
            "location_hubs", "scenes",
        ],
    }


__all__ = ["gemini_dance_schema"]
