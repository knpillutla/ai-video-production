"""Deterministic unit tests for FalAuraSRAdapter and 4K Keyframe Upscaling ($0.00 cost, offline)."""
import cv2
import numpy as np
import pytest
from pathlib import Path
from src.providers.visual.fal_aura_sr import FalAuraSRAdapter
from src.services.visual_batch_service import visual_batch_service


@pytest.fixture
def sample_keyframe(tmp_path: Path) -> Path:
    """Create a sample 1344x768 16:9 keyframe."""
    img_path = tmp_path / "sample_keyframe_p1.jpg"
    img = np.zeros((768, 1344, 3), dtype=np.uint8)
    # Draw simple gradient
    img[:, :] = np.linspace(40, 200, 1344, dtype=np.uint8)[None, :, None]
    cv2.imwrite(str(img_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return img_path


@pytest.mark.asyncio
async def test_aura_sr_adapter_offline_resizing(sample_keyframe: Path, tmp_path: Path):
    """Verify FalAuraSRAdapter produces exact 3840x2160 4K output in offline/mock mode."""
    out_4k = tmp_path / "keyframe_p1_4k.jpg"
    adapter = FalAuraSRAdapter(api_key=None)

    res = await adapter.upscale_image(sample_keyframe, out_4k, target_res=(3840, 2160))
    assert res == out_4k
    assert out_4k.is_file()
    assert out_4k.stat().st_size > 10_000

    img_4k = cv2.imread(str(out_4k))
    assert img_4k is not None
    assert img_4k.shape == (2160, 3840, 3), f"Expected (2160, 3840, 3), got {img_4k.shape}"


@pytest.mark.asyncio
async def test_aura_sr_cache_hit(sample_keyframe: Path, tmp_path: Path):
    """Verify artifact cache hit skips processing (Rule 3)."""
    out_4k = tmp_path / "keyframe_cached.jpg"
    # Pre-create large file
    out_4k.write_bytes(b"\xFF\xD8\xFF" + b"\x00" * 90_000)

    adapter = FalAuraSRAdapter(api_key=None)
    res = await adapter.upscale_image(sample_keyframe, out_4k)
    assert res == out_4k


@pytest.mark.asyncio
async def test_visual_batch_service_with_4k_upscale(tmp_path: Path, monkeypatch):
    """Verify visual_batch_service.render_keyframes_batch upscales keyframe to 4K."""
    out_kf = tmp_path / "batch_keyframe_p1.jpg"
    tasks = [("Cinematic European Alpine Lake", out_kf, None, 1)]

    from src.providers.visual.google_imagen3 import GoogleImagen3Adapter

    monkeypatch.setattr(visual_batch_service.__class__, "fal_key", property(lambda self: ""))
    monkeypatch.setattr("src.services.visual_batch_service._fal_api_key", lambda: "")
    monkeypatch.setattr("src.providers.fal_storage._fal_api_key", lambda: "")
    monkeypatch.setattr("src.providers.visual.fal_aura_sr._fal_api_key", lambda: "")

    async def _mock_gen(self, prompt, output_path, aspect_ratio="16:9", **kwargs):
        img = np.zeros((768, 1344, 3), dtype=np.uint8)
        cv2.imwrite(str(output_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return output_path

    monkeypatch.setattr(GoogleImagen3Adapter, "generate_to_file", _mock_gen)

    results = await visual_batch_service.render_keyframes_batch(
        tasks,
        aspect_ratio="16:9",
        force_rerun=True,
        image_model="gemini",
        enable_4k_upscale=True,
    )

    assert len(results) == 1
    assert results[0].is_file()
    img = cv2.imread(str(results[0]))
    assert img is not None
    assert img.shape == (2160, 3840, 3), f"Keyframe batch must produce 4K (2160, 3840, 3), got {img.shape}"
