"""Unit tests for the reusable 4K image encoder utility (Rule 8: $0.00 spend)."""

from pathlib import Path
import cv2
import numpy as np
import pytest

from src.services.image_4k_encoder import (
    ensure_image_4k,
    get_image_resolution,
    is_image_4k,
)


@pytest.fixture
def sample_720p_image(tmp_path: Path) -> Path:
    """Create a sample 1280x720 16:9 image."""
    img_path = tmp_path / "test_720p.jpg"
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    img[:, :] = (120, 180, 240)
    cv2.imwrite(str(img_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return img_path


@pytest.fixture
def sample_square_image(tmp_path: Path) -> Path:
    """Create a sample 1024x1024 1:1 image."""
    img_path = tmp_path / "test_square.jpg"
    img = np.zeros((1024, 1024, 3), dtype=np.uint8)
    img[:, :] = (200, 150, 100)
    cv2.imwrite(str(img_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return img_path


@pytest.fixture
def sample_portrait_image(tmp_path: Path) -> Path:
    """Create a sample 720x1280 9:16 image."""
    img_path = tmp_path / "test_portrait.jpg"
    img = np.zeros((1280, 720, 3), dtype=np.uint8)
    img[:, :] = (100, 200, 150)
    cv2.imwrite(str(img_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return img_path


@pytest.mark.asyncio
async def test_probe_and_upscale_16_9_to_4k(sample_720p_image: Path):
    """Verify that a 1280x720 image is detected as non-4k and upscaled to 3840x2160."""
    res_before = get_image_resolution(sample_720p_image)
    assert res_before == (1280, 720)
    assert not is_image_4k(sample_720p_image)

    res_path = await ensure_image_4k(sample_720p_image, aspect_ratio="16:9")
    assert res_path == sample_720p_image

    res_after = get_image_resolution(sample_720p_image)
    assert res_after == (3840, 2160)
    assert is_image_4k(sample_720p_image)


@pytest.mark.asyncio
async def test_probe_and_upscale_square_to_4k(sample_square_image: Path):
    """Verify that a 1024x1024 1:1 image is upscaled to 3840x3840 for LoRA datasets."""
    res_before = get_image_resolution(sample_square_image)
    assert res_before == (1024, 1024)
    assert not is_image_4k(sample_square_image)

    res_path = await ensure_image_4k(sample_square_image, aspect_ratio="1:1")
    assert res_path == sample_square_image

    res_after = get_image_resolution(sample_square_image)
    assert res_after == (3840, 3840)
    assert is_image_4k(sample_square_image)


@pytest.mark.asyncio
async def test_probe_and_upscale_portrait_to_4k(sample_portrait_image: Path):
    """Verify that a 720x1280 9:16 image is upscaled to 2160x3840 for Shorts."""
    res_before = get_image_resolution(sample_portrait_image)
    assert res_before == (720, 1280)
    assert not is_image_4k(sample_portrait_image)

    res_path = await ensure_image_4k(sample_portrait_image, aspect_ratio="9:16")
    assert res_path == sample_portrait_image

    res_after = get_image_resolution(sample_portrait_image)
    assert res_after == (2160, 3840)
    assert is_image_4k(sample_portrait_image)


@pytest.mark.asyncio
async def test_already_4k_image_is_noop(sample_720p_image: Path):
    """Verify that calling ensure_image_4k on an already 4K image is an immediate no-op."""
    await ensure_image_4k(sample_720p_image, aspect_ratio="16:9")
    assert is_image_4k(sample_720p_image)

    mtime_1 = sample_720p_image.stat().st_mtime
    await ensure_image_4k(sample_720p_image, aspect_ratio="16:9")
    mtime_2 = sample_720p_image.stat().st_mtime
    assert mtime_1 == mtime_2


@pytest.mark.asyncio
async def test_missing_image_handling(tmp_path: Path):
    """Verify graceful handling of non-existent image paths."""
    missing = tmp_path / "non_existent.jpg"
    assert not is_image_4k(missing)
    res = await ensure_image_4k(missing)
    assert res == missing
