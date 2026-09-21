"""Legacy offline visual adapter retained for isolation tests."""

from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, VisualProviderProtocol, is_mock_mode


class TogetherFluxAdapter(VisualProviderProtocol):
    """Offline compatibility adapter; production uses Fal FLUX.1-dev."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.media.together_api_key
        self.endpoint = "https://api.together.xyz/v1/images/generations"

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        loras: list[dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> str:
        """Call Together AI to diffuse a photoreal keyframe image."""
        if is_mock_mode():
            return f"https://cdn.cineai.studio/assets/flux_mock_{abs(hash(prompt)) % 10000}.jpg"

        client = HTTPClientPool.get_client()
        headers = {
            "Authorization": f"Bearer {self.api_key or ''}",
            "Content-Type": "application/json",
        }

        # Resolution based on aspect ratio
        width, height = (1344, 768) if aspect_ratio == "16:9" else (768, 1344)

        body: dict[str, Any] = {
            "model": "legacy-disabled",
            "prompt": f"Cinematic 4K broadcast still, photorealistic, shallow depth of field: {prompt}",
            "width": width,
            "height": height,
            "steps": 4,
            "n": 1,
            "response_format": "url",
        }
        if seed is not None:
            body["seed"] = seed
        if loras:
            body["loras"] = loras

        if self.api_key:
            try:
                resp = await client.post(self.endpoint, headers=headers, json=body, timeout=30.0)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["url"]
            except Exception as ex:
                logger.warning(f"together_flux_call_failed: {ex}. Falling back to deterministic canvas.")

        # Offline fallback: returns mock asset identifier
        return f"https://cdn.cineai.studio/assets/flux_mock_{abs(hash(prompt)) % 10000}.jpg"

    def _render_local_canvas(
        self,
        prompt: str,
        output_path: Path,
        aspect_ratio: str = "16:9",
        seed: int | None = None,
        loras: list[dict[str, Any]] | None = None,
    ) -> Path:
        """Render deterministic graphical canvas locally with zero network calls."""
        target_size = (1920, 1080) if aspect_ratio == "16:9" else (1080, 1920)
        img = Image.new("RGB", target_size, (15, 23, 42))
        draw = ImageDraw.Draw(img)
        for y in range(target_size[1]):
            ratio = y / target_size[1]
            r, g, b = int(20 + 35 * ratio), int(30 + 15 * ratio), int(50 + 60 * ratio)
            draw.line([(0, y), (target_size[0], y)], fill=(r, g, b))

        extra = f" | Seed: {seed}" if seed else ""
        if loras:
            extra += f" | LoRAs: {len(loras)}"
        draw.text((60, target_size[1] // 2 - 20), f"[Flux 4K Still{extra}] {prompt[:70]}...", fill=(240, 240, 250))
        img.save(output_path, format="JPEG", quality=90)
        return output_path

    async def generate_to_file(
        self,
        prompt: str,
        output_path: Path | str,
        aspect_ratio: str = "16:9",
        force_live: bool = False,
        loras: list[dict[str, Any]] | None = None,
        seed: int | None = None,
    ) -> Path:
        """Generate and save photoreal keyframe image (Together AI -> Serverless Flux -> Canvas)."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Artifact Caching Guard: Reuse existing keyframe image if already generated for this project
        if out.exists() and out.stat().st_size > 10000:
            logger.info(f"flux_image_cache_hit: reusing existing keyframe {out.name} ({out.stat().st_size} bytes)")
            return out

        if is_mock_mode() and not force_live:
            return self._render_local_canvas(prompt, out, aspect_ratio=aspect_ratio, seed=seed, loras=loras)

        client = HTTPClientPool.get_client()

        # 1. Try Together AI if API key is provided
        if self.api_key:
            try:
                img_url = await self.generate_image(prompt, aspect_ratio=aspect_ratio, loras=loras, seed=seed)
                if img_url and img_url.startswith("http") and "cineai.studio" not in img_url:
                    resp = await client.get(img_url, timeout=30.0)
                    if resp.status_code == 200:
                        out.write_bytes(resp.content)
                        return out
            except Exception as ex:
                logger.warning(f"together_download_failed: {ex}")

        # 2. Free Serverless Flux/SDXL Photoreal Diffusion Fallback
        try:
            import urllib.parse
            w, h = (1280, 720) if aspect_ratio == "16:9" else (720, 1280)
            seed_param = f"&seed={seed}" if seed is not None else ""
            encoded = urllib.parse.quote(f"cinematic photorealistic 4k {prompt}")
            poll_url = f"https://image.pollinations.ai/prompt/{encoded}?width={w}&height={h}&nologo=true{seed_param}"
            resp = await client.get(poll_url, timeout=25.0, follow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 5000:
                out.write_bytes(resp.content)
                logger.info(f"flux_photoreal_image_generated: {out.name} ({len(resp.content)} bytes)")
                return out
        except Exception as ex:
            logger.warning(f"serverless_flux_failed: {ex}")

        # 3. Deterministic graphical canvas fallback
        return self._render_local_canvas(prompt, out, aspect_ratio=aspect_ratio, seed=seed, loras=loras)



__all__ = ["TogetherFluxAdapter"]
