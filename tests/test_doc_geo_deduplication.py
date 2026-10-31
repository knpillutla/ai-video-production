"""Deterministic offline unit tests for Geo Rotation Deduplication and Vault Cache.

Guarantees 100% deterministic test execution ($0.00 model cost, Rule 8).
"""

from pathlib import Path
import pytest

from src.studios.documentary_studio.doc_geo_cache import (
    get_visited_entities,
    record_visited_entity,
    select_next_unvisited_entity,
)
from src.studios.documentary_studio.doc_geo_rotation import (
    resolve_autonomous_geo_details,
    resolve_autonomous_geo_entity,
)


def test_select_next_unvisited_entity_excludes_visited(tmp_path: Path, monkeypatch):
    """Test that select_next_unvisited_entity strictly skips visited countries."""
    pool = ["Poland", "Czech Republic", "Austria", "Italy", "France", "Spain", "Portugal", "Germany"]
    visited = {"poland", "czech republic", "austria", "italy", "france", "spain"}

    import src.studios.documentary_studio.doc_geo_cache as dgc
    monkeypatch.setattr(dgc, "get_visited_entities", lambda sg, cat, uid=None, cid=None: visited)

    # Mock recent topics containing Poland & France
    recent_topics = ["France: Citadels & Pioneers", "Poland: Heritage"]

    # When visited includes France and Spain, next pick must be Portugal
    next_entity, is_recycled = select_next_unvisited_entity(
        pool=pool,
        sub_genre="europe_nations",
        category="countries",
        recent_topics=recent_topics,
    )
    # The first entity in pool not in visited is Portugal
    assert next_entity.lower() not in visited
    assert next_entity == "Portugal"
    assert is_recycled is False


def test_custom_user_prompt_takes_precedence_over_rotation():
    """Test that if the user explicitly specifies a destination in their prompt, it is honored."""
    eff_genre, eff_arch, theme_title, selected_entity = resolve_autonomous_geo_details(
        sub_genre="europe_nations",
        archetype="country_profile",
        custom_prompt="Germany Castles, Medieval Citadels & Visionaries",
    )
    assert selected_entity == "Germany"
    assert "Germany" in theme_title


def test_visited_entities_scans_disk_directories(tmp_path: Path, monkeypatch):
    """Test that existing folders on disk under network documentary are automatically treated as visited."""
    from src.core.storage import storage_service

    # Create dummy network structure
    dummy_net = tmp_path / "euro_discovery"
    dummy_doc = dummy_net / "documentary"
    (dummy_doc / "france").mkdir(parents=True)
    (dummy_doc / "spain").mkdir(parents=True)
    (dummy_doc / "italy").mkdir(parents=True)

    monkeypatch.setattr(storage_service, "get_network_path", lambda uid, cid: dummy_net)

    visited = get_visited_entities(
        sub_genre="europe_nations",
        category="countries",
        user_id="test_user",
        channel_id="euro_discovery",
    )
    assert "france" in visited
    assert "spain" in visited
    assert "italy" in visited


def test_supermarkets_archetype_resolution():
    """Verify supermarkets archetype resolves cleanly with title templates and directives."""
    from src.studios.documentary_studio.doc_nations_archetypes import get_nations_archetype_directive

    eff_genre, eff_arch, theme_title, selected_entity = resolve_autonomous_geo_details(
        sub_genre="europe_nations",
        archetype="supermarkets",
        custom_prompt="France Supermarket Culture",
    )
    assert selected_entity == "France"
    assert "Supermarket" in theme_title
    directive = get_nations_archetype_directive("supermarkets")
    assert "SUPERMARKETS & GROCERY CULTURE" in directive
    assert "hypermarkets" in directive.lower()

