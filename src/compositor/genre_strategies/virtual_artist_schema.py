"""Schema definition for Virtual Artist Multi-Camera Concert Broadcasting.

Defines the structured output contract for:
1. Multi-camera stage rig setup (5-6 physical camera perspectives).
2. Broadcast switching timeline (3.5s - 5.0s cuts synchronized to song sections).
3. Singing vs orchestra classification (is_singing, active_instrument).
Preserves Rule 4 (< 300 lines limit).
"""

from __future__ import annotations


def virtual_artist_gemini_schema() -> dict:
    """Return strict JSON schema for Virtual Artist Multi-Camera Concert Broadcast."""
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

    camera_rig_scene = {
        "type": "OBJECT",
        "properties": {
            "scene_index": {"type": "INTEGER"},
            "camera_id": {
                "type": "STRING",
                "enum": [
                    "center_vocalist_front",
                    "stage_profile_45",
                    "vocal_close_up",
                    "drone_audience_focus",
                    "active_instrument_macro",
                    "high_crane_arena_vista",
                ],
            },
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
        "required": ["scene_index", "camera_id", "location_hub", "character_pose", "camera_shot_type", "visual_prompt"],
    }

    broadcast_cut = {
        "type": "OBJECT",
        "properties": {
            "cut_index": {"type": "INTEGER"},
            "start_time": {"type": "NUMBER"},
            "end_time": {"type": "NUMBER"},
            "duration_seconds": {"type": "NUMBER"},
            "camera_id": {
                "type": "STRING",
                "enum": [
                    "center_vocalist_front",
                    "stage_profile_45",
                    "vocal_close_up",
                    "drone_audience_focus",
                    "active_instrument_macro",
                    "high_crane_arena_vista",
                ],
            },
            "is_singing": {"type": "BOOLEAN"},
            "active_instrument": {"type": "STRING"},
            "lyrics_line": {"type": "STRING"},
            "local_drone_motion": {"type": "STRING"},
            "transition": {"type": "STRING", "enum": ["cut", "crossfade"]},
        },
        "required": ["cut_index", "start_time", "end_time", "duration_seconds", "camera_id", "is_singing"],
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
            "youtube_metadata": youtube_meta,
            "scenes": {"type": "ARRAY", "items": camera_rig_scene},
            "broadcast_timeline": {"type": "ARRAY", "items": broadcast_cut},
        },
        "required": [
            "title_en", "title_localized", "hook_thesis", "suno_tags",
            "vocal_gender", "lyrics", "prompts_by_model", "characters",
            "lyrics_segments", "youtube_metadata", "scenes", "broadcast_timeline",
        ],
    }


__all__ = ["virtual_artist_gemini_schema"]
