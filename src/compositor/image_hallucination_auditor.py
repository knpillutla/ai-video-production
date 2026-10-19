"""Automated Image Hallucination & Anatomy Quality Auditor.

Uses Gemini Flash Multimodal Vision to inspect synthesized keyframe images
for human anatomical defects (extra hands, 3 arms, floating limbs, deformed fingers)
and triggers automatic deletion & regeneration.
"""

from __future__ import annotations

import asyncio
import base64
from io import BytesIO
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.providers.base import HTTPClientPool, is_mock_mode
from src.providers.llm.gemini_adapter import get_live_gemini_api_key


class ImageAuditResult(BaseModel):
    """Evaluation result from multimodal visual anatomical audit."""

    is_valid: bool = Field(default=True, description="False if anatomical hallucination or defect detected")
    has_hallucinations: bool = Field(default=False, description="True if extra limbs, floating hands, or deformities found")
    defects: list[str] = Field(default_factory=list, description="Specific defects identified")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Model confidence score")
    reason: str = Field(default="Normal human anatomy", description="Audit explanation")


_AUDIT_PROMPT = """Analyze this image with extreme scrutiny for AI diffusion hallucinations and anatomical errors:
1. Count visible hands and wrists of each person. Does any character have duplicate hands, overlapping ghost hands, or an extra hand? Look closely at hands resting on knees, laps, or hips. Check for duplicate wrists or an extra third hand.
2. Count wristwatches on each character. Does any person have TWO wristwatches (one above the other, or two wrists each wearing a watch)? A person must wear at most ONE watch.
3. Extra limbs: Check for 3+ arms, extra legs, or disembodied limbs floating detached from any person.
4. Severely deformed hands: Check for 6+ fingers, fused webbed claw fingers, or grotesque distorted hands.
5. Conjoined or duplicate bodies (two torsos fused, conjoined heads, duplicate body parts).

Note: Ignore normal artistic background elements, crowd members in distant bokeh blur, and cultural props. Focus strictly on whether foreground characters exhibit anatomical hallucinations, duplicate hands, or extra limbs.

Return JSON in this exact structure:
{
  "is_valid": boolean,
  "has_hallucinations": boolean,
  "defects": ["description of defect 1", ...],
  "confidence": 0.95,
  "reason": "summary explanation"
}
"""


async def audit_image_anatomy(
    image_path: Path | str,
    prompt_context: str = "",
    force_live: bool = False,
    max_dimension: int = 1024,
) -> ImageAuditResult:
    """Inspect an image for anatomical hallucinations and extra limbs using Gemini Flash Vision."""
    path = Path(image_path)
    if not path.is_file() or path.stat().st_size < 1000:
        return ImageAuditResult(is_valid=False, has_hallucinations=True, reason="Image file missing or empty")

    if is_mock_mode() and not force_live:
        return ImageAuditResult(is_valid=True, has_hallucinations=False, reason="Offline mock mode bypass")

    api_key = get_live_gemini_api_key()
    if not api_key:
        logger.warning("image_hallucination_auditor: no Gemini API key found, bypassing vision audit")
        return ImageAuditResult(is_valid=True, has_hallucinations=False, reason="No API key available")

    try:
        from PIL import Image

        with Image.open(path) as img:
            img_copy = img.copy()
            img_copy.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            buf = BytesIO()
            img_copy.convert("RGB").save(buf, format="JPEG", quality=80)
            b64_data = base64.b64encode(buf.getvalue()).decode("utf-8")

        client = HTTPClientPool.get_client()
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
        body: dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"inlineData": {"mimeType": "image/jpeg", "data": b64_data}},
                        {"text": _AUDIT_PROMPT},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        resp = await client.post(url, params={"key": api_key}, json=body, timeout=20.0)
        if resp.status_code != 200:
            logger.warning(f"image_audit_http_status_{resp.status_code}: bypassing audit for {path.name}")
            return ImageAuditResult(is_valid=True, has_hallucinations=False, reason=f"HTTP {resp.status_code} bypass")

        data = resp.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = json.loads(raw_text)

        has_hallucinations = bool(parsed.get("has_hallucinations", False))
        is_valid = bool(parsed.get("is_valid", not has_hallucinations))
        defects = list(parsed.get("defects", []))
        confidence = float(parsed.get("confidence", 1.0))
        reason = str(parsed.get("reason", "Anatomy verified"))

        # If model detected hallucination with high confidence, mark invalid
        if has_hallucinations and confidence >= 0.65:
            is_valid = False

        result = ImageAuditResult(
            is_valid=is_valid,
            has_hallucinations=has_hallucinations,
            defects=defects,
            confidence=confidence,
            reason=reason,
        )
        if not result.is_valid:
            logger.warning(
                f"image_hallucination_detected: file={path.name}, defects={result.defects}, reason='{result.reason}'"
            )
        else:
            logger.info(f"image_hallucination_cleared: file={path.name}, reason='{result.reason}'")
        return result

    except Exception as exc:
        logger.warning(f"image_hallucination_audit_failed: {exc}. Permitting image to proceed.")
        return ImageAuditResult(is_valid=True, has_hallucinations=False, reason=f"Audit exception: {exc}")


__all__ = ["ImageAuditResult", "audit_image_anatomy"]
