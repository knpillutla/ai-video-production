"""Schema definition for Vocal Song & Lyrical Video Gemini Storyboard.

Defines the structured output contract for characters, lyrics segments,
prompts by model, animation timelines, and scenes.
"""

from __future__ import annotations


def vocal_gemini_schema() -> dict:
    """Return strict JSON schema for vocal lyrical video structured output."""
    character = {
        "type": "OBJECT",
        "properties": {
            "name": {"type": "STRING"},
            "gender": {"type": "STRING"},
            "age": {"type": "INTEGER"},
            "body_composition": {"type": "STRING"},
            "hair_and_facial_features": {"type": "STRING"},
            "outfit_description": {"type": "STRING"},
        },
        "required": ["name", "gender", "age", "body_composition", "outfit_description"],
    }
    lyrics_seg = {
        "type": "OBJECT",
        "properties": {
            "start": {"type": "NUMBER"},
            "end": {"type": "NUMBER"},
            "text": {"type": "STRING"},
            "text_en": {"type": "STRING"},
        },
        "required": ["start", "end", "text", "text_en"],
    }
    prompts_model = {
        "type": "OBJECT",
        "properties": {
            "z_image": {"type": "STRING"},
            "flux_dev": {"type": "STRING"},
            "flux_pro_ultra": {"type": "STRING"},
            "imagen3": {"type": "STRING"},
            "midjourney": {"type": "STRING"},
        },
        "required": ["z_image", "flux_dev", "flux_pro_ultra", "imagen3", "midjourney"],
    }
    youtube_meta = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "description": {"type": "STRING"},
            "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
            "pinned_comment": {"type": "STRING"},
            "thumbnail_prompt": {"type": "STRING"},
            "category_id": {"type": "STRING"},
        },
        "required": ["title", "description", "tags", "pinned_comment"],
    }
    anim_cue = {
        "type": "OBJECT",
        "properties": {
            "start_time": {"type": "NUMBER"},
            "end_time": {"type": "NUMBER"},
            "musical_phase": {"type": "STRING"},
            "camera_motion": {"type": "STRING"},
            "effect_type": {"type": "STRING"},
            "intensity": {"type": "STRING"},
            "rationale": {"type": "STRING"},
        },
        "required": ["start_time", "end_time", "camera_motion", "effect_type"],
    }
    return {
        "type": "OBJECT",
        "properties": {
            "title_en": {"type": "STRING"},
            "title_localized": {"type": "STRING"},
            "song_type": {"type": "STRING"},
            "mood": {"type": "STRING"},
            "language": {"type": "STRING"},
            "country": {"type": "STRING"},
            "tempo_bpm": {"type": "INTEGER"},
            "hook_thesis": {"type": "STRING"},
            "suno_tags": {"type": "STRING"},
            "vocal_gender": {"type": "STRING"},
            "lyrics": {"type": "STRING"},
            "prompts_by_model": prompts_model,
            "characters": {"type": "ARRAY", "items": character},
            "lyrics_segments": {"type": "ARRAY", "items": lyrics_seg},
            "animation_timeline": {"type": "ARRAY", "items": anim_cue},
            "youtube_metadata": youtube_meta,
            "scenes": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "scene_index": {"type": "INTEGER"},
                        "duration_seconds": {"type": "NUMBER"},
                        "location_hub": {"type": "STRING"},
                        "character_pose": {"type": "STRING"},
                        "camera_shot_type": {"type": "STRING"},
                        "camera_motion": {"type": "STRING"},
                        "camera_speed": {"type": "STRING", "enum": ["slow", "medium", "fast", "steady"]},
                        "local_drone": {
                            "type": "OBJECT",
                            "properties": {
                                "movement": {"type": "STRING"},
                                "speed": {"type": "STRING", "enum": ["slow", "medium", "fast", "steady"]},
                                "parallel_movements": {"type": "ARRAY", "items": {"type": "STRING"}},
                                "start_pan": {"type": "STRING"},
                                "start_zoom": {"type": "STRING"},
                                "start_tilt": {"type": "STRING"},
                                "rationale": {"type": "STRING"},
                            },
                        },
                        "visual_prompt": {"type": "STRING"},
                        "dialogue": {"type": "STRING"},
                        "render_mode": {"type": "STRING", "enum": ["motion", "still"]},
                        "motion_prompts": {
                            "type": "OBJECT",
                            "properties": {
                                "wan": {"type": "STRING"},
                                "kling": {"type": "STRING"},
                            },
                        },
                    },
                    "required": ["scene_index", "duration_seconds", "location_hub", "character_pose", "camera_shot_type", "visual_prompt"],
                },
            },
        },
        "required": [
            "title_en", "title_localized", "hook_thesis", "suno_tags",
            "vocal_gender", "lyrics", "prompts_by_model", "characters",
            "lyrics_segments", "youtube_metadata", "scenes",
        ],
    }


__all__ = ["vocal_gemini_schema"]
