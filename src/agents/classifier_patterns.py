"""Deterministic keyword and semantic pattern tables for classification."""

from src.domain.generation import MediaFormat, ThemeGenre, VisualStyle

THEME_PATTERNS: list[tuple[ThemeGenre, list[str]]] = [
    (ThemeGenre.TELUGU_COMEDY, ["comedy", "confusions", "wfh", "standup", "office", "prank", "satire", "fun", "joke", "telugu", "hyderabad"]),
    (ThemeGenre.HISTORICAL_EPIC, ["kingdom", "war for a kingdom", "medieval", "crusade", "empire", "dynasty", "monarch", "throne", "crown", "conquest"]),
    (ThemeGenre.FANTASY, ["fantasy", "dragon", "magic", "sorcerer", "realm", "mythical", "celestial", "avatar", "spell", "warlock", "elven", "beast"]),
    (ThemeGenre.EPIC_ACTION, ["action", "battle", "sword", "warrior", "elevation", "interval", "mass", "clash", "fight", "revenge", "rebel", "yodha", "protector"]),
    (ThemeGenre.BOLLYWOOD_DANCE, ["dance", "folk dance", "village dance", "jathara", "dappu", "hook step", "choreography", "beat drop", "song", "celebration", "sangeet", "musical", "bollywood", "rhythm", "telangana", "folk", "village"]),
    (ThemeGenre.NATURE_WILDLIFE, ["tiger", "leopard", "wildlife", "safari", "nature", "forest", "predator", "ocean", "jungle", "himalayas", "fauna", "rainforest", "rain forest", "fjord", "fjord norway", "beautiful norway", "iceland", "amazon"]),
    (ThemeGenre.TRAVEL_TOURISM, ["travel", "tourism", "destination", "vlog", "explore", "journey", "backpacking", "resort", "monument", "itinerary", "attractions", "tourist", "sightseeing", "places to visit", "heritage", "guide", "walking tour", "walk", "hiking", "trekking", "tourist attractions", "top 10 places", "in 3 days", "in 4 days"]),
    (ThemeGenre.ROMANTIC_DRAMA, ["romance", "love", "heartbreak", "wedding", "relationship", "couple", "emotional", "crush", "dating", "lover", "romantic"]),
    (ThemeGenre.TECH_SCIFI, ["cyberpunk", "ai", "robot", "future", "matrix", "neural", "sci-fi", "quantum", "cyborg", "dystopia", "silicon", "metaverse"]),
]

STYLE_PATTERNS: list[tuple[VisualStyle, list[str]]] = [
    (VisualStyle.ANIME, ["anime", "manga", "shonen", "toonify", "chibi", "otaku", "makoto", "ghibli", "cel shaded"]),
    (VisualStyle.ANIMATION_3D, ["3d", "cgi", "pixar", "disney", "animated 3d", "render", "character rig"]),
    (VisualStyle.STYLIZED_COMIC, ["comic", "graphic novel", "noir", "sketch", "comicbook", "illustrated"]),
    (VisualStyle.REALISTIC, ["realistic", "cinematic", "photorealistic", "4k", "8k", "live action", "portrait", "documentary"]),
]

FORMAT_PATTERNS: list[tuple[MediaFormat, list[str]]] = [
    (MediaFormat.WALKING_TOUR, [
        "walking tour", "walk tour", "trail walk", "city walk", "foot tour", "scenic walk", "hike tour", "walking in", "walk through",
    ]),
    (MediaFormat.TRAVEL_GUIDE, [
        "tourist attractions", "top attractions", "attractions", "tourist spots", "places to visit", "sightseeing", "top 10 spots", "top 10 places", "top places",
        "things to do in", "monument tour", "guide", "in 3 days", "in 4 days", "in 5 days", "city guide", "travel guide", "tourism",
    ]),
    (MediaFormat.NATURE_SANCTUARY, [
        "nature documentary", "beautiful norway", "mountaineous norway", "fjord norway", "amazon rain forest", "rain forest",
        "iceland journey", "beautiful places", "untamed", "wild planet", "wildlife sanctuary", "safari journey",
    ]),
    (MediaFormat.DANCE_VIDEO, [
        "dance video", "dance song", "dance", "hook step", "choreography", "beat drop", "song dance",
        "mass dance", "mass song", "mass jathara", "jathara", "folk dance", "party dance", "family dance", "dancers",
    ]),
    (MediaFormat.MUSIC_VIDEO, [
        "music video", "monsoon song", "love song", "melody song", "romantic song", "lyric video", "song video",
    ]),
    (MediaFormat.MOVIE_CINEMATIC, [
        "movie", "cinema", "feature film", "short film", "blockbuster", "trailer", "yodha", "the protector",
        "war for a kingdom", "kingdom in uk", "action movie", "fantasy movie",
    ]),
    (MediaFormat.EPIC_CINEMATIC, [
        "epic", "bahubali", "avatar", "grandeur", "monumental", "vfx film", "historical epic",
    ]),
    (MediaFormat.MOUNTAIN_SURVIVAL, [
        "survival", "blizzard", "mountain survival", "extreme weather", "shepherd", "frost", "subzero",
    ]),
    (MediaFormat.VLOG, [
        "vlog", "travel vlog", "day in the life", "solo travel", "road trip",
    ]),
    (MediaFormat.NEWS_TABLOID, [
        "breaking news", "tabloid", "report", "bulletin", "headline", "scandal", "news",
    ]),
    (MediaFormat.PODCAST_EXPLAINER, [
        "podcast", "explainer", "breakdown", "deep dive", "interview", "discussion", "talk show",
    ]),
    (MediaFormat.WEB_SERIES, [
        "web series", "webseries", "episode", "ep ", "series", "wfh confusions", "sitcom", "part 1", "season",
    ]),
]
