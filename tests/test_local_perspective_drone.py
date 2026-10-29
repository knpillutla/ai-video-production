"""Deterministic offline unit tests for CPU perspective drone & camera homography motion engine."""

import numpy as np
import pytest
from src.scripts.local_perspective_drone import (
    normalize_choreography_sequence,
    precompute_sequence_matrices,
)


def test_precompute_sequence_matrices_forward():
    seq = [("dollyin", 5.0)]
    matrices, total_frames = precompute_sequence_matrices(
        img_shape=(2160, 3840, 3),
        sequence=seq,
        fps=24.0,
        output_size=(3840, 2160),
    )
    assert total_frames == 120
    assert len(matrices) == 120
    assert matrices[0].shape == (3, 3)


def test_precompute_sequence_matrices_stay():
    seq = [("stay", 5.0)]
    matrices, total_frames = precompute_sequence_matrices(
        img_shape=(2160, 3840, 3),
        sequence=seq,
        fps=24.0,
        output_size=(3840, 2160),
    )
    assert total_frames == 120
    # For pure locked stay, transformation matrices should be invariant across time
    assert np.allclose(matrices[0], matrices[-1], atol=1e-3)


def test_normalize_choreography_sequence_timeline_and_stages():
    from src.scripts.local_perspective_drone import normalize_choreography_sequence

    # Sequential timeline array format
    seq_input = [
        {"movement": "dollyin", "duration": 6.0},
        {"movement": "zoomin", "duration": 4.0},
    ]
    norm = normalize_choreography_sequence(seq_input, default_duration=10.0)
    assert len(norm) == 2
    assert norm[0] == ("dollyin", 6.0)
    assert norm[1] == ("zoomin", 4.0)

    # Gemini stage format with parallel movement
    stage_input = [
        {"stage": 1, "duration": 5.0, "movements": ["dollyin", "pan-right"]},
        {"stage": 2, "duration": 5.0, "movements": ["tilt-up"]},
    ]
    norm_stages = normalize_choreography_sequence(stage_input, default_duration=10.0)
    assert len(norm_stages) == 2
    assert norm_stages[0][0] == "parallel"
    assert norm_stages[1] == ("tilt-up", 5.0)

    # Relaxation locked hold format
    relax_input = [{"movement": "stay", "duration": 10.0}]
    norm_relax = normalize_choreography_sequence(relax_input, default_duration=10.0)
    assert norm_relax == [("stay", 10.0)]

    # Documentary screenplay parallel + sequential format with extended movements
    doc_input = [
        {"duration": 10.0, "parallel": ["slow-drone-forward", "tilt-down"]},
        {"duration": 9.8, "motion": "crane-ascend"},
    ]
    norm_doc = normalize_choreography_sequence(doc_input, default_duration=19.8)
    assert norm_doc[0] == ("parallel", [("slow-drone-forward", 10.0), ("tilt-down", 10.0)])
    assert norm_doc[1] == ("crane-ascend", 9.8)


def test_living_environment_engine_water_and_clouds():
    from src.scripts.local_perspective_drone import LivingEnvironmentEngine

    # Synthetic 480x270 image with bright cloudy upper sky and blue water in lower half
    img = np.zeros((270, 480, 3), dtype=np.uint8)
    img[:110, :] = (225, 220, 215)  # Light cloud sky
    img[140:, :] = (160, 110, 40)   # BGR blue water body
    eng = LivingEnvironmentEngine(img, 480, 270, enable_water=True, enable_clouds=True, total_frames=120)
    assert eng.living_world.has_any is True
    p0 = eng.get_source_plate(0)
    p36 = eng.get_source_plate(36)
    assert p0.shape == (270, 480, 3)
    # Continuous non-repeating animation: frame 36 differs from frame 0 (no 36-frame snap-back)
    assert not np.array_equal(p0, p36)




