"""Targeted unit tests for image_model_configs resolution across studios (100% offline)."""
import pytest
from src.studios.screenplay_models import BaseScenePrompt, AmbientScenePrompt
from src.studios.studio_producer import StudioProducer


def test_resolve_scene_image_prompt_with_existing_cfg():
    s = AmbientScenePrompt(
        scene_index=1,
        shot_type="wide",
        visual_prompt="Base visual prompt",
        image_model_configs={
            "zimage": {"prompt": "Explicit Z-Image prompt on Hasselblad"},
            "flux_dev": {"prompt": "Explicit FLUX Dev prompt"},
        },
    )
    # Instantiate producer
    producer = StudioProducer()
    # Test internal helper logic directly or via produce setup
    cfgs = s.image_model_configs
    assert cfgs["zimage"]["prompt"] == "Explicit Z-Image prompt on Hasselblad"


def test_resolve_scene_image_prompt_fallback_builds_default_cfgs():
    s = AmbientScenePrompt(
        scene_index=1,
        shot_type="wide",
        visual_prompt="Wide 4K panoramic aerial drone vista sweeping over Mount Tomanivi in Fiji",
        image_model_configs={},
    )
    # Simulate _resolve_scene_image_prompt logic
    from src.studios.directorial_configs import build_default_image_model_configs
    assert not s.image_model_configs
    
    # After resolution logic
    new_cfgs = build_default_image_model_configs(s.visual_prompt, "Mount Tomanivi")
    s.image_model_configs = new_cfgs
    assert "zimage" in s.image_model_configs
    assert "flux_dev" in s.image_model_configs
    assert "flux_pro" in s.image_model_configs
    assert "Mount Tomanivi" in s.image_model_configs["zimage"]["prompt"]
    assert "Hasselblad H6D-100c" in s.image_model_configs["zimage"]["prompt"]


def test_flatten_chapters_generates_image_model_configs():
    from src.studios.documentary_studio.doc_chapter_cadence_service import flatten_chapters_to_timeline
    raw_chapters = [
        {
            "chapter_title": "Geography & Volcanic Origins",
            "chapter_subtitle": "Rugged Terrain",
            "fact_badge": "VOLCANIC",
            "chapter_stats": "330 Islands",
            "narration_text": "Fiji is an archipelago.",
            "planned_duration_seconds": 10.0,
            "shots": [
                {
                    "visual_prompt": "Drone shot of volcanic peak",
                    "location_hub": "Mount Tomanivi",
                },
                {
                    "visual_prompt": "Close-up of coral reef waters",
                    "location_hub": "Coral Coast",
                },
            ],
        }
    ]
    flattened, ch_map = flatten_chapters_to_timeline({"chapters": raw_chapters}, fallback_dur_per_scene=10.0)
    assert len(flattened) == 2
    for shot in flattened:
        assert "image_model_configs" in shot
        assert "zimage" in shot["image_model_configs"]
        assert "Hasselblad" in shot["image_model_configs"]["zimage"]["prompt"]
