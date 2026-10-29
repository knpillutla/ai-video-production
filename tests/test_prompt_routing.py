"""Tests for Extensible Format/Genre/Sub-Genre/Archetype Prompt Routing Engine."""
from pathlib import Path
from src.core.prompt_routing_service import resolve_prompt_file, get_prompt_blueprint


def test_resolve_country_overview_story_and_screenplay_prompts():
    """Verify that country_overview resolves to distinct story and screenplay prompt files."""
    story_p = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_overview", stage="story")
    assert story_p.name == "country_overview.prompt.md"
    assert story_p.exists()

    screenplay_p = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_overview", stage="screenplay")
    assert screenplay_p.name == "country_overview.screenplay.prompt.md"
    assert screenplay_p.exists()

    # Aliases
    alias_story = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_dossier", stage="story")
    assert alias_story.name == "country_overview.prompt.md"

    alias_sp = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_dossier", stage="screenplay")
    assert alias_sp.name == "country_overview.screenplay.prompt.md"


def test_resolve_country_encyclopedia_prompts():
    """Verify that country_encyclopedia resolves distinct story and screenplay files."""
    story_p = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_encyclopedia", stage="story")
    assert story_p.name == "country_encyclopedia.prompt.md"
    assert story_p.exists()

    screenplay_p = resolve_prompt_file("documentary", "doc/nations", "europe_nations", "country_encyclopedia", stage="screenplay")
    assert screenplay_p.name == "country_encyclopedia.screenplay.prompt.md"
    assert screenplay_p.exists()


def test_resolve_civilizational_origins_prompts():
    """Verify that Indus Valley civilization resolves distinct story and screenplay files."""
    story_p = resolve_prompt_file("documentary", "doc/civilizations", "indus_vedic", "civilizational_origins", stage="story")
    assert story_p.name == "civilizational_origins.prompt.md"
    assert story_p.exists()

    screenplay_p = resolve_prompt_file("documentary", "doc/civilizations", "indus_vedic", "civilizational_origins", stage="screenplay")
    assert screenplay_p.name == "civilizational_origins.screenplay.prompt.md"
    assert screenplay_p.exists()

    content = get_prompt_blueprint("documentary", "doc/civilizations", "indus_vedic", "civilizational_origins", stage="screenplay")
    assert "Cinematographer" in content or "Visual" in content


def test_documentary_base_prompt_composition():
    """Verify that documentary story blueprint composes Universal Base Prompt with Archetype Blueprint."""
    blueprint = get_prompt_blueprint("documentary", "doc/nations", "europe_nations", "country_overview", stage="story")
    # Must contain base instructions
    assert "Universal Base Documentary Story Directorial Blueprint" in blueprint
    assert "Top 4 to 5 premier universities" in blueprint
    assert "Capital City" in blueprint
    # Must contain archetype instructions
    assert "21-Chapter Sovereign Country Overview" in blueprint or "Sovereign Pillars" in blueprint
