"""Centralized Screenplay Execution Engine for Studio Directors.

Handles the Google Gemini API lifecycle, strict zero-fallback failure enforcement,
raw artifact persistence, and tier-validated schema modeling.
Studio directors must only supply genre directives and delegate execution here.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
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
    from src.providers.llm.gemini_adapter import get_live_gemini_api_key
    api_key = get_live_gemini_api_key()
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

    masked_key = f"{api_key[:2]}...{api_key[-2:]}" if (api_key and len(api_key) >= 4) else "none"
    client = HTTPClientPool.get_client()
    logger.info(f"gemini_screenplay_engine_request: key='{masked_key}' tier='{eff_tier}' genre='{genre}' archetype='{primary_archetype}' search={google_search_enabled}")

    try:
        resp = await client.post(url, json=payload, timeout=180.0)
    except Exception as net_err:
        err_desc = f"{type(net_err).__name__}: {net_err}" if str(net_err) else type(net_err).__name__
        logger.error(f"gemini_network_error: key='{masked_key}' {err_desc}")
        raise RuntimeError(f"Gemini API request failed due to network exception (key: {masked_key}): {err_desc}") from net_err

    if resp.status_code != 200:
        err_msg = f"Gemini API error (HTTP {resp.status_code}): {resp.text[:500]}"
        logger.error(f"gemini_api_failure: key='{masked_key}' status={resp.status_code} body='{resp.text[:200]}'")
        raise RuntimeError(f"Production halted: Screenplay formulation failed (key: {masked_key}): {err_msg}")

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Production halted: Gemini returned empty candidates list with zero screenplay content.")

    raw_json = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    if raw_json.startswith("```"):
        lines = raw_json.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_json = "\n".join(lines).strip()
    if not raw_json:
        raise RuntimeError("Production halted: Gemini returned empty content text in candidate.")

    # 1. Guarantee raw JSON artifact is persisted as pure truth from LLM
    if raw_output_path:
        try:
            raw_p = Path(raw_output_path)
            raw_p.parent.mkdir(parents=True, exist_ok=True)
            raw_p.write_text(raw_json, encoding="utf-8")
            logger.info(f"raw_gemini_screenplay_artifact_saved: {raw_p}")
            sp_inputs_payload = {
                "model": "gemini-flash-latest",
                "tier": eff_tier,
                "genre": genre,
                "sub_genre": sub_genre,
                "cluster": cluster,
                "primary_archetype": primary_archetype,
                "google_search_enabled": google_search_enabled,
                "system_prompt": sys_prompt,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            (raw_p.parent / "gemini_screenplay_inputs.json").write_text(
                json.dumps(sp_inputs_payload, indent=2, ensure_ascii=False), encoding="utf-8"
            )
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
