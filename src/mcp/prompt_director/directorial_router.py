"""Tier 0 Deterministic Directorial Prompt Router & Template Assembler."""

from pathlib import Path
from typing import Any

TEMPLATES_DIR = Path(__file__).parent / "templates"

_TEMPLATE_CACHE: dict[str, str] = {}


def _get_template_text(template_name: str) -> str:
    """Retrieve template text from cache or disk."""
    if template_name not in _TEMPLATE_CACHE:
        file_path = TEMPLATES_DIR / template_name
        if file_path.exists():
            _TEMPLATE_CACHE[template_name] = file_path.read_text(encoding="utf-8")
        else:
            _TEMPLATE_CACHE[template_name] = ""
    return _TEMPLATE_CACHE[template_name]


def classify_directorial_mode(topic: str, genre: str = "", video_format: str = "") -> str:
    """Deterministic Tier 0 classifier for directorial category."""
    cues = f"{genre} {video_format} {topic}".lower()

    if any(k in cues for k in ("documentary", "wild", "wildlife", "planet", "earth", "untamed", "natural history", "national park", "ecosystem", "nature's")):
        if any(s in cues for s in ("blizzard", "shepherd", "survival", "trapped")):
            return "mountain_survival"
        return "nature_documentary"

    if any(k in cues for k in ("blizzard", "shepherd", "survival", "afghanistan", "mountain life", "snowstorm", "nomad", "extreme weather", "pamir")):
        return "mountain_survival"

    if any(k in cues for k in ("scenic", "walk", "drive", "relaxation", "lounge", "nature", "alps", "rain", "tour", "travel", "ambient", "forest", "waterfall", "village_walk")):
        return "scenic_narrative"

    if any(k in cues for k in ("music", "song", "folk", "dance", "mass", "tollywood_mass", "bollywood", "hiphop", "celebration", "festive", "choreo")):
        return "music_dance"

    if any(k in f"{genre} {video_format}".lower() for k in ("comedy", "satire", "sitcom", "drama", "web_series")):
        return "narrative_retention"

    if any(k in cues for k in ("tech", "code", "programming", "software", "ai", "tutorial", "architecture", "explainer", "guide", "how-to")):
        return "tech_explainer"

    return "narrative_retention"


def build_directorial_prompt(
    topic: str,
    genre: str = "comedy",
    video_format: str = "",
    style_name: str = "Broadcast 4K Photorealistic Cinematic",
    decorations: str = "",
    lighting: str = "",
    palette: str = "",
    guidance: str = "",
    target_duration_seconds: int = 60,
    language: str = "en",
) -> tuple[str, str]:
    """Assemble a hyper-focused directorial prompt tailored strictly to the matched mode."""
    mode = classify_directorial_mode(topic, genre, video_format)

    template_mapping = {
        "mountain_survival": "mountain_survival.md",
        "nature_documentary": "nature_documentary.md",
        "scenic_narrative": "scenic_walking_tour.md",
        "music_dance": "dance_choreography.md",
        "tech_explainer": "tech_explainer.md",
        "narrative_retention": "narrative_satire.md",
    }

    genre_template_name = template_mapping.get(mode, "narrative_satire.md")
    genre_template = _get_template_text(genre_template_name)
    base_contract = _get_template_text("base_contract.md")

    # Interpolate variables safely
    interpolated_genre = genre_template.format(
        topic=topic,
        genre=genre,
        video_format=video_format or mode.replace("_", " ").title(),
        style_name=style_name,
        decorations=decorations or "Photorealistic 4K broadcast standard",
        lighting=lighting or "Natural 5600K balanced daylight",
        palette=palette or "Authentic cinematic tones",
        guidance=guidance or "High audience retention",
        target_duration_seconds=target_duration_seconds,
        language=language,
    )

    assembled_prompt = f"{interpolated_genre.strip()}\n\n{base_contract.strip()}"
    return assembled_prompt, mode
