"""Content Style & Format Intelligence Classifier Agent.

Provides deterministic Tier 0 semantic classification with optional Tier 1 LLM fallback,
supporting automatic detection of Media Format, Visual Style, and Theme with 1-click user override.
"""

from src.core.telemetry import logger
from src.domain.generation import ContentClassification, MediaFormat, ThemeGenre, VisualStyle


# Tier 0 Deterministic Keyword & Semantic Pattern Tables
THEME_PATTERNS: list[tuple[ThemeGenre, list[str]]] = [
    (ThemeGenre.TELUGU_COMEDY, ["comedy", "confusions", "wfh", "standup", "office", "prank", "satire", "fun", "joke", "telugu", "hyderabad"]),
    (ThemeGenre.EPIC_ACTION, ["action", "battle", "sword", "warrior", "elevation", "interval", "mass", "clash", "fight", "revenge", "dynasty", "rebel"]),
    (ThemeGenre.BOLLYWOOD_DANCE, ["dance", "hook step", "choreography", "beat drop", "song", "celebration", "sangeet", "musical", "bollywood", "rhythm"]),
    (ThemeGenre.NATURE_WILDLIFE, ["tiger", "leopard", "wildlife", "safari", "nature", "forest", "predator", "ocean", "jungle", "himalayas", "fauna"]),
    (ThemeGenre.TRAVEL_TOURISM, ["travel", "tourism", "destination", "vlog", "explore", "journey", "backpacking", "resort", "monument", "itinerary", "attractions", "tourist", "sightseeing", "places to visit", "heritage", "guide"]),
    (ThemeGenre.ROMANTIC_DRAMA, ["romance", "love", "heartbreak", "wedding", "relationship", "couple", "emotional", "crush", "dating", "lover"]),
    (ThemeGenre.TECH_SCIFI, ["cyberpunk", "ai", "robot", "future", "matrix", "neural", "sci-fi", "quantum", "cyborg", "dystopia", "silicon", "metaverse"]),
]

STYLE_PATTERNS: list[tuple[VisualStyle, list[str]]] = [
    (VisualStyle.ANIME, ["anime", "manga", "shonen", "toonify", "chibi", "otaku", "makoto", "ghibli", "cel shaded"]),
    (VisualStyle.ANIMATION_3D, ["3d", "cgi", "pixar", "disney", "animated 3d", "render", "character rig"]),
    (VisualStyle.STYLIZED_COMIC, ["comic", "graphic novel", "noir", "sketch", "comicbook", "illustrated"]),
    (VisualStyle.REALISTIC, ["realistic", "cinematic", "photorealistic", "4k", "8k", "live action", "portrait", "documentary"]),
]

FORMAT_PATTERNS: list[tuple[MediaFormat, list[str]]] = [
    (MediaFormat.TRAVEL_GUIDE, ["travel guide", "city guide", "tourist attractions", "tourist spots", "places to visit", "sightseeing", "top 10 spots", "things to do in", "monument tour", "guide"]),
    (MediaFormat.VLOG, ["vlog", "travel vlog", "day in the life", "walking tour", "solo travel", "road trip"]),
    (MediaFormat.DANCE_VIDEO, ["dance video", "hook step", "choreography", "music video", "beat drop", "song dance"]),
    (MediaFormat.NEWS_TABLOID, ["breaking news", "tabloid", "report", "bulletin", "headline", "scandal", "news"]),
    (MediaFormat.PODCAST_EXPLAINER, ["podcast", "explainer", "breakdown", "deep dive", "interview", "discussion", "talk show"]),
    (MediaFormat.MOVIE_CINEMATIC, ["movie", "cinema", "feature film", "short film", "blockbuster", "trailer"]),
    (MediaFormat.WEB_SERIES, ["episode", "ep ", "series", "wfh confusions", "sitcom", "part 1", "season"]),
]


class ClassifierAgent:
    """Classifies script narratives and creative concepts into optimal format and visual styling."""

    def detect(self, text: str, title: str | None = None) -> ContentClassification:
        """Deterministically infer MediaFormat, VisualStyle, and ThemeGenre from text."""
        combined = f"{title or ''} {text}".lower().strip()
        logger.info(f"classifier_agent_detect: input_len={len(combined)}")

        # 1. Detect Theme
        detected_theme = ThemeGenre.TELUGU_COMEDY  # Default fallback
        theme_score = 0
        for theme, keywords in THEME_PATTERNS:
            matches = sum(1 for kw in keywords if kw in combined)
            if matches > theme_score:
                theme_score = matches
                detected_theme = theme

        # 2. Detect Visual Style
        detected_style = VisualStyle.REALISTIC
        style_score = 0
        for style, keywords in STYLE_PATTERNS:
            matches = sum(1 for kw in keywords if kw in combined)
            if matches > style_score:
                style_score = matches
                detected_style = style

        # 3. Detect Media Format
        detected_format = MediaFormat.WEB_SERIES
        format_score = 0
        for fmt, keywords in FORMAT_PATTERNS:
            matches = sum(1 for kw in keywords if kw in combined)
            if matches > format_score:
                format_score = matches
                detected_format = fmt

        # Format inference cross-rules based on detected theme
        if detected_theme == ThemeGenre.BOLLYWOOD_DANCE and format_score == 0:
            detected_format = MediaFormat.DANCE_VIDEO
        elif detected_theme in (ThemeGenre.EPIC_ACTION, ThemeGenre.NATURE_WILDLIFE) and format_score == 0:
            detected_format = MediaFormat.MOVIE_CINEMATIC

        confidence = min(0.98, max(0.80, 0.80 + (theme_score + style_score + format_score) * 0.04))
        explanation = (
            f"Auto-inferred: {detected_format.value.replace('_', ' ').title()} format, "
            f"{detected_style.value.title()} visual style, and {detected_theme.value.replace('_', ' ').title()} theme."
        )

        return ContentClassification(
            media_format=detected_format,
            visual_style=detected_style,
            theme=detected_theme,
            is_auto_detected=True,
            confidence=round(confidence, 2),
            explanation=explanation,
        )

    def resolve_classification(
        self,
        text: str,
        user_format: str | MediaFormat = MediaFormat.AUTO,
        user_style: str | VisualStyle = VisualStyle.AUTO,
        user_theme: str | ThemeGenre = ThemeGenre.AUTO,
        title: str | None = None,
    ) -> ContentClassification:
        """Resolve classification allowing explicit user selections to override AI inference."""
        inferred = self.detect(text, title=title)

        # Normalize string inputs if passed as strings
        req_format = MediaFormat(user_format) if isinstance(user_format, str) else user_format
        req_style = VisualStyle(user_style) if isinstance(user_style, str) else user_style
        req_theme = ThemeGenre(user_theme) if isinstance(user_theme, str) else user_theme

        # Determine effective values
        final_format = inferred.media_format if req_format == MediaFormat.AUTO else req_format
        final_style = inferred.visual_style if req_style == VisualStyle.AUTO else req_style
        final_theme = inferred.theme if req_theme == ThemeGenre.AUTO else req_theme

        overrides: list[str] = []
        if req_format != MediaFormat.AUTO:
            overrides.append(f"Format: {final_format.value}")
        if req_style != VisualStyle.AUTO:
            overrides.append(f"Style: {final_style.value}")
        if req_theme != ThemeGenre.AUTO:
            overrides.append(f"Theme: {final_theme.value}")

        is_auto = len(overrides) == 0
        explanation = (
            inferred.explanation
            if is_auto
            else f"User Overrides Applied: {', '.join(overrides)} (AI auto-detected remaining attributes)."
        )

        return ContentClassification(
            media_format=final_format,
            visual_style=final_style,
            theme=final_theme,
            is_auto_detected=is_auto,
            confidence=1.0 if not is_auto else inferred.confidence,
            explanation=explanation,
        )


classifier_agent = ClassifierAgent()
__all__ = ["ClassifierAgent", "classifier_agent"]
