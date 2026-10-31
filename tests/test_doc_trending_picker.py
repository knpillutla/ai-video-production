"""Targeted offline unit tests for autonomous trending destination picker ($0 spend)."""
from unittest.mock import patch
from src.studios.documentary_studio.doc_trending_picker import select_trending_geo_destination


def test_select_trending_geo_destination_offline():
    pool = ["Iceland", "Switzerland", "Norway", "Slovenia"]
    visited = ["iceland", "switzerland"]

    with patch("src.studios.documentary_studio.doc_trending_picker.get_visited_entities", return_value=visited):
        chosen, is_recycled = select_trending_geo_destination(
            pool=pool,
            sub_genre="europe_nations",
            archetype="country_overview",
        )
        assert chosen == "Norway"
        assert is_recycled is False


def test_select_trending_geo_destination_recent_topics_exclusion():
    pool = ["Iceland", "Switzerland", "Norway", "Slovenia"]
    visited = ["iceland"]
    recent = ["Norway: The Complete 360 Documentary"]

    with patch("src.studios.documentary_studio.doc_trending_picker.get_visited_entities", return_value=visited):
        chosen, is_recycled = select_trending_geo_destination(
            pool=pool,
            sub_genre="europe_nations",
            archetype="country_overview",
            recent_topics=recent,
        )
        assert chosen == "Switzerland"
        assert is_recycled is False


def test_select_trending_geo_destination_recycles_when_pool_exhausted():
    pool = ["Iceland", "Switzerland"]
    visited = ["iceland", "switzerland"]

    with patch("src.studios.documentary_studio.doc_trending_picker.get_visited_entities", return_value=visited):
        chosen, is_recycled = select_trending_geo_destination(
            pool=pool,
            sub_genre="europe_nations",
            archetype="country_overview",
        )
        assert chosen in pool
        assert is_recycled is True

