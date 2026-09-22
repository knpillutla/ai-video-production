"""Genre Strategy resolver — maps MediaFormat/genre to the right strategy implementation."""

from src.compositor.genre_strategies.base_strategy import GenreStrategy
from src.compositor.genre_strategies.comedy_strategy import ComedyStrategy
from src.compositor.genre_strategies.dance_strategy import DanceStrategy
from src.compositor.genre_strategies.epic_cinematic_strategy import EpicCinematicStrategy
from src.compositor.genre_strategies.mountain_survival_strategy import MountainSurvivalStrategy
from src.compositor.genre_strategies.music_video_strategy import MusicVideoStrategy
from src.compositor.genre_strategies.nature_strategy import NatureDocumentaryStrategy
from src.compositor.genre_strategies.tourist_guide_strategy import TouristGuideStrategy
from src.compositor.genre_strategies.walking_tour_strategy import WalkingTourStrategy

# Singleton instances — strategies are stateless config, instantiated once
_STRATEGIES: dict[str, GenreStrategy] = {
    "dance_video": DanceStrategy(),
    "music_video": MusicVideoStrategy(),
    "tourist_guide": TouristGuideStrategy(),
    "travel_guide": TouristGuideStrategy(),
    "tourist_attractions": TouristGuideStrategy(),
    "nature_documentary": NatureDocumentaryStrategy(),
    "nature_sanctuary": NatureDocumentaryStrategy(),
    "walking_tour": WalkingTourStrategy(),
    "scenic_relaxation": WalkingTourStrategy(),
    "scenic_drive": WalkingTourStrategy(),
    "ambient_lounge": WalkingTourStrategy(),
    "vlog": WalkingTourStrategy(),
    "web_series": ComedyStrategy(),
    "comedy": ComedyStrategy(),
    "podcast_explainer": ComedyStrategy(),
    "news_tabloid": ComedyStrategy(),
    "movie_cinematic": EpicCinematicStrategy(),
    "epic_cinematic": EpicCinematicStrategy(),
    "mountain_survival": MountainSurvivalStrategy(),
}

# Fallback keyword detection for when format string doesn't match directly
_KEYWORD_FALLBACKS: list[tuple[list[str], str]] = [
    (["dance", "folk dance", "jathara", "choreography", "song dance", "mass dance"], "dance_video"),
    (["music video", "monsoon song", "love song", "melody song"], "music_video"),
    (["tourist attractions", "top 10 places", "places to see", "city guide", "in 3 days", "in 4 days"], "tourist_guide"),
    (["nature", "wildlife", "safari", "jungle", "ocean", "forest"], "nature_documentary"),
    (["walk", "tour", "scenic", "drive", "travel", "ambient"], "walking_tour"),
    (["mountain", "survival", "blizzard", "shepherd", "extreme"], "mountain_survival"),
    (["epic", "battle", "warrior", "bahubali", "avatar", "blockbuster", "kingdom", "war for a kingdom"], "epic_cinematic"),
    (["comedy", "funny", "sitcom", "office", "wfh", "confusions"], "web_series"),
]

_DEFAULT = ComedyStrategy()


def resolve_strategy(
    media_format: str = "",
    genre: str = "",
    idea: str | None = None,
) -> GenreStrategy:
    """Resolve the right genre strategy from format, genre, and idea text.

    Precedence:
    1. Explicit specialized media_format match in _STRATEGIES (non-generic)
    2. Strong keyword match from genre + idea text
    3. Exact media_format match in _STRATEGIES
    4. Default comedy/web_series strategy
    """
    fmt = media_format.lower().strip()
    if fmt in _STRATEGIES and fmt not in ("web_series", "comedy", "auto", ""):
        return _STRATEGIES[fmt]

    # Keyword check — scan genre + idea for cues
    combined = f"{genre} {idea or ''}".lower()
    for keywords, strategy_key in _KEYWORD_FALLBACKS:
        if any(kw in combined for kw in keywords):
            return _STRATEGIES[strategy_key]

    if fmt in _STRATEGIES:
        return _STRATEGIES[fmt]

    return _DEFAULT


__all__ = [
    "GenreStrategy", "resolve_strategy",
    "DanceStrategy", "NatureDocumentaryStrategy", "WalkingTourStrategy",
    "ComedyStrategy", "MountainSurvivalStrategy", "EpicCinematicStrategy",
    "TouristGuideStrategy", "MusicVideoStrategy",
]
