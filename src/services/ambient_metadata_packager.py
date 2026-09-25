"""High-CTR YouTube Metadata, Chapters, Pinned Comments, and Thumbnail Packaging."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class YouTubeAmbientPackage(BaseModel):
    """Complete YouTube packaging for maximum CTR, AVD, and SEO ranking."""
    title: str
    description: str
    tags: List[str] = Field(default_factory=list)
    thumbnail_prompt: str
    chapter_markers: List[str] = Field(default_factory=list)
    pinned_comment: str


TITLE_TEMPLATES: Dict[str, str] = {
    "swiss_alps": "Swiss Alps Rain & Distant Thunder ~ Cozy Chalet Sleep in Lauterbrunnen [4K, 432Hz]",
    "himalayas": "Sacred Himalayas Deep Meditation ~ 432Hz Monastery Wind & Tibetan Singing Bowls [4K]",
    "ocean_world": "Underwater Coral Paradise ~ Calming Deep Sea Bioluminescence for Instant Sleep [4K]",
    "mountains": "Misty Mountain Sunrise ~ Soothing Alpine Breeze & Deep Sleep Resonance [4K, 432Hz]",
    "rain": "Gentle Forest River Rain ~ Ultra-Soft Raindrops for Insomnia Relief & Deep Study [4K]",
    "lake": "Placid Mountain Lake at Dawn ~ Serene Water Reflections & Calming Morning Mist [4K]",
    "beach": "Tropical Beach Sunset Waves ~ Velvet Ocean Surf & Gentle Sea Breeze for Sleep [4K]",
    "camp_fire": "Starlit Campfire & Milky Way ~ Cozy Crackling Hearth Under the Stars [4K, 432Hz]",
    "forest": "Ancient Pine Forest Sunbeams ~ Soothing Woodland Breeze & Golden Dawn Birds [4K]",
    "beach_house": "Cozy Beach House Storm ~ Velvet Rain on Ocean Waves for Instant Rest [4K, 432Hz]",
    "night_sleep": "Moonlit Celestial Night Sky ~ 432Hz Delta Waves for 8 Hours of Unbroken Sleep [4K]",
    "blizzard": "Sub-Zero Mountain Blizzard Outside ~ Warm Fireplace Inside Timber Cabin [4K, 432Hz]",
    "winter": "Pristine Winter Snowfall ~ Gentle Falling Snow in Quiet Evergreen Forest [4K]",
    "autumn": "Golden Autumn Rain on River ~ Crimson Maple Leaves & Cozy Forest Stream [4K]",
}


def generate_youtube_ambient_package(
    archetype_key: str,
    duration_hours: float = 1.0,
    secondary_element: Optional[str] = None,
    fade_to_black_hours: Optional[float] = None,
) -> YouTubeAmbientPackage:
    """Generate high-CTR YouTube metadata, thumbnail prompt, and chapter timestamps."""
    key = archetype_key.lower().replace("-", "_").replace(" ", "_")
    base_title = TITLE_TEMPLATES.get(key, f"Cozy {archetype_key.title()} ~ 4K Velvet Sleep Ambiance [432Hz]")
    
    if secondary_element:
        base_title = f"{base_title.split('~')[0]}with {secondary_element.title()} ~{base_title.split('~')[1]}"

    if fade_to_black_hours:
        base_title = f"{base_title.split('[')[0]}~ Fades to Black Screen after {int(fade_to_black_hours)}H [{base_title.split('[')[1]}"

    # Chapter Markers
    num_hours = int(duration_hours) or 1
    chapters = [
        "00:00:00 🌿 Golden Hour Relaxation & Settling In",
        "00:30:00 🌧️ Velvet Rain & Calming Ambiance",
    ]
    for h in range(1, num_hours + 1):
        if fade_to_black_hours and h == int(fade_to_black_hours):
            chapters.append(f"{h:02d}:00:00 🌑 Screen Fades to Pure Black (Audio Continues)")
        elif h == 1:
            chapters.append("01:00:00 🌙 432Hz Delta Wave Sleep Transition")
        elif h == 3:
            chapters.append("03:00:00 💤 Deep REM Sleep & Unbroken Rest")
        elif h == 6:
            chapters.append("06:00:00 ✨ Early Dawn Peaceful Awakening")

    description = (
        f"Immerse yourself in this 4K Velvet Ambient Soundscape featuring {archetype_key.replace('_', ' ').title()}.\n\n"
        "✨ Acoustic Engineering: Mastered to -21.0 LUFS with Velvet Low-Pass anti-fatigue filtering "
        "and sub-audible 432Hz delta wave brainwave entrainment to ease insomnia and promote deep restorative sleep.\n\n"
        "⏰ Sleep Chapters:\n" + "\n".join(chapters) + "\n\n"
        "🎧 For optimal relaxation and sleep, listen with headphones at comfortable volume.\n"
        "🌿 100% Commercial Master Rights | 4K UHD Visuals"
    )

    thumb_prompt = (
        f"High-contrast masterpiece YouTube thumbnail photograph of {archetype_key.replace('_', ' ')}. "
        "Striking color contrast between warm glowing golden amber light inside and deep atmospheric cool cobalt blue outside. "
        "Extreme visual depth, crisp 35mm optical bokeh, cozy inviting mood, award-winning cinematography, 8k, zero text."
    )

    pinned_comment = (
        f"🌿 Welcome to your nightly sanctuary. Leave a comment with one thing you are grateful for today, "
        "put on your headphones, set your sleep timer, and rest deeply. Sleep chapters are listed in the description. 🌙💤"
    )

    tags = [
        archetype_key, "relaxing_music", "deep_sleep", "432hz", "sleep_meditation",
        "4k_nature", "ambient_soundscape", "asmr", "insomnia_relief", "fades_to_black_screen"
    ]

    return YouTubeAmbientPackage(
        title=base_title,
        description=description,
        tags=tags,
        thumbnail_prompt=thumb_prompt,
        chapter_markers=chapters,
        pinned_comment=pinned_comment,
    )
