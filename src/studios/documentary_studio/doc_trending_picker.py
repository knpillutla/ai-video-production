"""Autonomous Trending Geo-Entity Picker powered by Gemini.

Replaces mechanical round-robin rotation with editorial intelligence:
Directs Gemini to analyze current travel search trends, cultural fascination,
and high-CTR documentary intrigue across unvisited destinations.
"""
from __future__ import annotations

import json
import logging
import re
from typing import List, Optional, Tuple

from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter, get_live_gemini_api_key
from src.studios.documentary_studio.doc_geo_cache import get_visited_entities

logger = logging.getLogger("video_studio")


def select_trending_geo_destination(
    pool: List[str],
    sub_genre: str,
    archetype: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    recent_topics: Optional[List[str]] = None,
    custom_prompt: Optional[str] = None,
) -> Tuple[str, bool]:
    """Select the #1 most compelling, high-CTR, currently trending destination via Gemini.

    Excludes previously covered destinations (from disk directories and Topic Memory).
    In mock/test mode or if Gemini is offline, falls back deterministically ($0.00 spend).
    Returns (selected_entity, is_recycled).
    """
    if not pool:
        return "Unknown", False

    category = "cities" if archetype in ("cities", "city") else "countries"
    visited = get_visited_entities(sub_genre, category, user_id, channel_id)
    seen_text = " ".join(recent_topics or []).lower()

    # Filter pool to strictly unvisited candidates
    available = [
        cand for cand in pool
        if cand.lower().strip() not in visited and cand.lower().strip() not in seen_text
    ]

    is_recycled = False
    if not available:
        logger.warning(f"geo_pool_exhausted: all {len(pool)} entities visited in '{sub_genre}'. Recycling pool.")
        available = list(pool)
        is_recycled = True

    # Deterministic mock fallback for offline tests / missing API keys
    api_key = get_live_gemini_api_key()
    if is_mock_mode() or not api_key:
        return available[0], is_recycled

    # In live mode: Direct Gemini to evaluate current trends and viewer curiosity
    try:
        adapter = GeminiLLMAdapter(api_key=api_key)
        prompt = (
            "You are the Executive Editorial Director for BBC / National Geographic international documentary broadcasts.\n"
            "Autonomously analyze and select the #1 most compelling, high-CTR, currently trending destination for our next 4K documentary feature.\n\n"
            f"CONTINENT / SUB-GENRE: {sub_genre}\n"
            f"DOCUMENTARY ARCHETYPE: {archetype}\n"
            f"AVAILABLE CANDIDATE DESTINATIONS:\n{json.dumps(available)}\n\n"
            f"EXCLUDED (ALREADY PRODUCED):\n{json.dumps(list(visited)[:25]) if visited else 'None'}\n\n"
            f"THEME / AUDIENCE GUIDANCE:\n{custom_prompt or 'None - prioritize natural majesty, cultural depth, and viral curiosity'}\n\n"
            "EDITORIAL DIRECTIVES:\n"
            "1. Select exactly ONE destination from the AVAILABLE CANDIDATE DESTINATIONS list. Do NOT invent a name outside this list.\n"
            "2. Prioritize destinations with surging global travel interest, dramatic natural or cultural paradoxes, and highest curiosity CTR.\n"
            "3. Output valid minified JSON only:\n"
            '{"selected_entity": "<exact name from candidates>", "rationale": "<1 sentence why it is trending right now>"}'
        )

        import asyncio
        loop = asyncio.get_event_loop() if asyncio.get_event_loop().is_running() else None
        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                raw_resp = executor.submit(asyncio.run, adapter.generate_text(prompt, temperature=0.4)).result(timeout=15.0)
        else:
            raw_resp = asyncio.run(adapter.generate_text(prompt, temperature=0.4))

        match = re.search(r"\{.*\}", raw_resp, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            chosen = parsed.get("selected_entity", "").strip()
            # Verify candidate matches an item in available list (case-insensitive)
            for cand in available:
                if cand.lower() == chosen.lower():
                    logger.info(f"gemini_trending_destination_selected: '{cand}' (rationale: {parsed.get('rationale')})")
                    return cand, is_recycled
    except Exception as ex:
        logger.warning(f"gemini_trending_selection_failed: {ex}. Falling back to top unvisited candidate.")

    return available[0], is_recycled

