"""Test Suite for TrendingPlanner Service."""

import pytest
from src.services.trending_planner import TrendingPlanner, TrendingCandidate, TRENDING_SEED_CATALOG


@pytest.mark.asyncio
async def test_trending_planner_discovery():
    """Verify TrendingPlanner discovers categorized, monetization-ready topics."""
    planner = TrendingPlanner(language="en")
    candidates = await planner.fetch_trending_candidates(categories=["travel", "nature"], max_results=3)

    assert len(candidates) > 0
    for cand in candidates:
        assert isinstance(cand, TrendingCandidate)
        assert cand.title
        assert cand.idea
        assert cand.monetization_ready is True
        assert cand.similarity_score < 0.80


@pytest.mark.asyncio
async def test_trending_planner_ocean_category():
    """Verify ocean abyss candidates are correctly discovered."""
    planner = TrendingPlanner(language="en")
    candidates = await planner.fetch_trending_candidates(categories=["ocean"], max_results=2)

    assert len(candidates) > 0
    assert any("ocean" in c.category.lower() or "abyss" in c.title.lower() or "coral" in c.title.lower() for c in candidates)
