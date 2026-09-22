"""Autonomous Trending Discovery, Deduplication & Monetization Planner Service."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from src.compliance.ypp_safety import evaluate_ypp_safety
from src.core.telemetry import logger
from src.mcp.topic_memory.server import check_topic_duplicate, recent_topic_context
from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter


@dataclass
class TrendingCandidate:
    """Ranked trending video topic with monetization clearance and deduplication verification."""
    topic_id: str
    category: str
    title: str
    idea: str
    estimated_ctr: str
    target_format: str = "walking_tour"
    monetization_ready: bool = True
    similarity_score: float = 0.0
    editorial_thesis: str = ""


TRENDING_SEED_CATALOG: dict[str, list[dict[str, str]]] = {
    "nature": [
        {
            "title": "4K Cascading Waterfalls & Emerald Canyon Walk in Lauterbrunnen Valley",
            "idea": "4K walking tour through Lauterbrunnen Switzerland with 72 roaring glacial waterfalls, wooden chalet cottages, and mist",
            "format": "walking_tour",
            "thesis": "Geological erosion history of glacier valleys and Alpine hydrology",
        },
        {
            "title": "Secrets of the Ancient Redwood Canopy: Giant Sequoia Rainforest Expedition",
            "idea": "4K cinematic nature documentary through California ancient coastal redwoods with sunbeams and morning fog",
            "format": "documentary",
            "thesis": "Ecosystem biodiversity and multi-century resilience of redwood root networks",
        },
    ],
    "ocean": [
        {
            "title": "The 11,000-Meter Abyss: Secrets of the Mariana Trench & Midnight Zone",
            "idea": "Deep sea ocean documentary exploring the Mariana Trench, hydrothermal vents, and bioluminescent creatures in the abyss",
            "format": "documentary",
            "thesis": "Deep-sea extreme pressure adaptations and hydrothermal chemical synthesis",
        },
        {
            "title": "Bora Bora Coral Atoll & Azure Ocean Lagoon Marine Sanctuary",
            "idea": "4K tranquil ocean coastal walk and coral reef exploration with crystal turquoise waters and overwater bungalows",
            "format": "walking_tour",
            "thesis": "Coral polyps symbiotic reef ecosystems and Polynesian marine conservation",
        },
    ],
    "travel": [
        {
            "title": "4K Heavy Rain Walking Tour: Historic Paris Montmartre Twilight & Cozy Cafes",
            "idea": "4K heavy rain walking tour through historic Paris Montmartre with wet cobblestone reflections and glowing cafe awnings",
            "format": "walking_tour",
            "thesis": "19th-century Parisian Belle Époque bohemian artists and architectural history",
        },
        {
            "title": "Hallstatt Austria 4K Walking Tour: The Most Beautiful Village in the World",
            "idea": "4K walking tour of Hallstatt Austria alpine village with ancient timber houses, swans on the glassy lake, and mountain mist",
            "format": "walking_tour",
            "thesis": "Ancient prehistoric salt mine settlements and alpine lake geology",
        },
        {
            "title": "Trastevere Rome 4K Evening Walk: Hidden Cobblestone Alleys & Ancient Piazzas",
            "idea": "4K sunset walking tour through Rome Trastevere with ivy-covered medieval arches, warm street lamps, and bustling trattorias",
            "format": "walking_tour",
            "thesis": "Roman medieval urban planning, Tiber river history, and Italian culinary traditions",
        },
    ],
}


class TrendingPlanner:
    """Discovers viral, high-retention video topics, enforcing deduplication and YPP compliance."""

    def __init__(self, user_id: str | None = None, language: str = "en") -> None:
        self.user_id = user_id
        self.language = language
        self.llm = GeminiLLMAdapter()

    async def fetch_trending_candidates(
        self,
        categories: list[str] | None = None,
        max_results: int = 5,
    ) -> list[TrendingCandidate]:
        """Discover and rank monetization-compliant, non-duplicate trending topics."""
        active_cats = categories or ["travel", "nature", "ocean"]
        excluded = recent_topic_context(self.user_id, self.language)
        candidates: list[TrendingCandidate] = []

        raw_items: list[dict[str, str]] = []
        for cat in active_cats:
            raw_items.extend(TRENDING_SEED_CATALOG.get(cat.lower().strip(), []))

        if not is_mock_mode() and len(candidates) < max_results:
            try:
                exclusions_text = "; ".join(excluded[-10:]) if excluded else "none yet"
                dyn_prompt = (
                    f"Discover {max_results} viral, high-CTR YouTube video concepts for categories: {', '.join(active_cats)}. "
                    f"Prioritize 4K walking tours, blue-chip nature, ocean abyss, and scenic world travel. "
                    f"Strictly exclude prior topics: {exclusions_text}. "
                    f"Return a valid JSON array of objects with keys: title, idea, category, format, thesis, estimated_ctr."
                )
                resp = await self.llm.generate_text(
                    dyn_prompt,
                    system_prompt="You are a YouTube viral travel & nature strategist specializing in high-RPM, monetization-safe documentaries.",
                    temperature=0.85,
                )
                clean_json = resp.strip().strip("`").removeprefix("json").strip()
                parsed = json.loads(clean_json)
                if isinstance(parsed, list):
                    raw_items.extend(parsed)
            except Exception as ex:
                logger.warning(f"trending_dynamic_discovery_fallback: {ex}")

        for item in raw_items:
            if len(candidates) >= max_results:
                break
            title = item.get("title", "4K Scenic World Walk")
            idea = item.get("idea", title)
            cat = item.get("category", "travel")
            fmt = item.get("format", "walking_tour")
            thesis = item.get("thesis", "Educational historical and ecological commentary")

            dup_meta = {"category": cat, "format": fmt, "language": self.language}
            check = await check_topic_duplicate(idea, metadata=dup_meta, user_id=self.user_id, language=self.language)
            sim_score = check.get("max_similarity_score", 0.0)
            if check.get("is_duplicate", False) or sim_score >= 0.80:
                logger.info(f"trending_candidate_duplicate_skipped: '{title}' (sim={sim_score:.2f})")
                continue

            mon_check = evaluate_ypp_safety(f"{title}. {thesis}")

            candidates.append(
                TrendingCandidate(
                    topic_id=f"trend_{uuid4().hex[:8]}",
                    category=cat,
                    title=title,
                    idea=idea,
                    estimated_ctr=item.get("estimated_ctr", "8.5% - 12.0%"),
                    target_format=fmt,
                    monetization_ready=mon_check.get("is_monetization_safe", True),
                    similarity_score=sim_score,
                    editorial_thesis=thesis,
                )
            )

        logger.info(f"trending_candidates_discovered: count={len(candidates)} categories={active_cats}")
        return candidates


__all__ = ["TrendingCandidate", "TrendingPlanner", "TRENDING_SEED_CATALOG"]
