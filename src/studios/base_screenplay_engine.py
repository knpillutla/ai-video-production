"""Centralized Screenplay Execution Engine for Studio Directors.

Handles the Google Gemini API lifecycle, strict zero-fallback failure enforcement,
raw artifact persistence, and tier-validated schema modeling.
Studio directors must only supply genre directives and delegate execution here.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool
from src.studios.screenplay_models import RelaxScreenplay


async def execute_directorial_screenplay(
    sys_prompt: str,
    raw_output_path: Optional[os.PathLike | str] = None,
    tier: str = "balanced",
    genre: Optional[str] = None,
    cluster: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    sub_genre: Optional[str] = None,
    google_search_enabled: bool = False,
) -> RelaxScreenplay:
    """Execute Gemini prompt, persist raw JSON artifact, enforce zero fallbacks, and validate RelaxScreenplay."""
    api_key = settings.llm.google_api_key or settings.llm.gemini_api_key
    if not api_key:
        raise RuntimeError("Production halted: Google Gemini API key is missing or not configured in environment.")

    eff_tier = (tier or "balanced").strip().lower()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    payload: dict = {
        "contents": [{"parts": [{"text": sys_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7,
        },
    }
    if google_search_enabled:
        payload["tools"] = [{"google_search": {}}]

    client = HTTPClientPool.get_client()
    logger.info(f"gemini_screenplay_engine_request: tier='{eff_tier}' genre='{genre}' archetype='{primary_archetype}' search={google_search_enabled}")

    try:
        resp = await client.post(url, json=payload, timeout=120.0)
    except Exception as net_err:
        err_desc = f"{type(net_err).__name__}: {net_err}" if str(net_err) else type(net_err).__name__
        logger.error(f"gemini_network_error: {err_desc}")
        raise RuntimeError(f"Gemini API request failed due to network exception: {err_desc}") from net_err

    if resp.status_code != 200:
        err_msg = f"Gemini API error (HTTP {resp.status_code}): {resp.text[:500]}"
        logger.error(f"gemini_api_failure: status={resp.status_code} body='{resp.text[:200]}'")
        raise RuntimeError(f"Production halted: Screenplay formulation failed: {err_msg}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Production halted: Gemini returned empty candidates list with zero screenplay content.")

    raw_json = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    if not raw_json:
        raise RuntimeError("Production halted: Gemini returned empty content text in candidate.")

    # 1. Guarantee raw JSON artifact is persisted as pure truth from LLM
    if raw_output_path:
        try:
            raw_p = Path(raw_output_path)
            raw_p.parent.mkdir(parents=True, exist_ok=True)
            raw_p.write_text(raw_json, encoding="utf-8")
            logger.info(f"raw_gemini_screenplay_artifact_saved: {raw_p}")
            grounding = candidates[0].get("groundingMetadata")
            if grounding:
                grounding_path = raw_p.with_suffix(".grounding.json")
                grounding_path.write_text(json.dumps(grounding, indent=2), encoding="utf-8")
                logger.info(f"gemini_grounding_metadata_saved: {grounding_path}")
        except Exception as raw_save_err:
            logger.warning(f"failed_to_save_raw_gemini_screenplay_artifact: {raw_save_err}")

    # 2. Parse and validate schema
    try:
        parsed = json.loads(raw_json)
    except Exception as parse_err:
        logger.error(f"gemini_invalid_json: {parse_err}")
        raise RuntimeError(f"Production halted: Gemini output is not valid JSON: {parse_err}") from parse_err

    if not isinstance(parsed, dict):
        raise RuntimeError("Production halted: Gemini JSON payload must be an object matching RelaxScreenplay.")

    # Ensure tier is explicitly present in validated output
    if "tier" not in parsed or not parsed["tier"]:
        parsed["tier"] = eff_tier

    screenplay = RelaxScreenplay.model_validate(parsed)
    if genre:
        screenplay.genre = genre
    if cluster:
        screenplay.cluster = cluster
    if primary_archetype:
        screenplay.primary_archetype = primary_archetype
    if sub_genre:
        screenplay.sub_genre = sub_genre
    screenplay.tier = eff_tier

    return screenplay
