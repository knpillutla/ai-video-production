"""Growth & SEO Agent for high-CTR localized thumbnails, tags, and YouTube metadata."""

from pathlib import Path
from typing import Any
from src.core.telemetry import logger
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail



class GrowthSEOAgent:
    """Specialized Agent for audience growth, localized A/B thumbnails, and search optimization."""

    def generate_growth_metadata(
        self,
        title: str,
        topic: str,
        genre: str = "comedy",
        language: str = "te",
    ) -> dict[str, Any]:
        """Generate high-CTR clickable title variants, search tags, and YouTube description."""
        title_variants = [
            f"Why Everyone Is Talking About: {title}",
            f"{title} - The Hidden Truth!",
            f"You Won't Believe What Happened: {title}",
        ]

        tags = [
            genre.capitalize(),
            f"{genre.capitalize()}2026",
            "TeluguComedy" if language == "te" else "HindiComedy" if language == "hi" else "ViralVideo",
            "WFH",
            "Trending",
            "Shorts",
            "CineAI",
            topic.split()[0] if topic.split() else "DailyComedy",
        ]

        description = (
            f"🔥 {title}\n\n"
            f"Dive into this brand-new episode exploring '{topic}' with authentic storytelling, "
            f"high-production visuals, and regional comedic timing.\n\n"
            f"🔔 Subscribe to the channel for daily episodes!\n"
            f"#shorts #{genre} #trending"
        )

        return {
            "primary_title": title,
            "title_variants": title_variants,
            "search_tags": tags,
            "description": description,
            "language": language,
        }

    def render_localized_thumbnail(
        self,
        base_image_path: Path | str,
        output_path: Path | str,
        episode_number: int = 1,
        language: str = "te",
        headline_text: str = "MUST WATCH!",
    ) -> Path:
        """Render high-contrast localized thumbnail with non-obscured top-left episodic badge."""
        cfg = EpisodicBadgeConfig(
            episode_number=episode_number,
            language=language,
            style="pill",
        )
        return generate_episodic_thumbnail(
            output_path=output_path,
            base_image_path=base_image_path,
            badge_config=cfg,
            headline=headline_text,
        )



growth_seo_agent = GrowthSEOAgent()

__all__ = ["GrowthSEOAgent", "growth_seo_agent"]
