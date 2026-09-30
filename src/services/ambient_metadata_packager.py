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
    "swiss_alps": "Swiss Alps Rain & Distant Thunder • Cozy Chalet Ambience in 4K",
    "himalayas": "Sacred Himalayas Ambience • Calming Mountain Wind & Monastery Bowls [4K]",
    "ocean_world": "Underwater Coral Paradise • Calming Deep Sea Sanctuary in 4K",
    "mountains": "Misty Mountain Sunrise • Soothing Alpine Breeze & Deep Peace [4K]",
    "rain": "Gentle Forest River Rain • Soft Raindrops for Sleep & Study [4K]",
    "lake": "Placid Mountain Lake at Dawn • Serene Water Reflections & Morning Mist [4K]",
    "beach": "Tropical Beach Sunset Waves • Velvet Ocean Surf & Gentle Sea Breeze [4K]",
    "camp_fire": "Starlit Campfire & Milky Way • Cozy Crackling Hearth Under Stars [4K]",
    "forest": "Ancient Pine Forest Sunbeams • Soothing Woodland Breeze in 4K",
    "beach_house": "Cozy Beach House Rain • Calming Waves & Window Raindrops [4K]",
    "night_sleep": "Moonlit Celestial Night Sky • Starry Cosmos & Deep Relaxation [4K]",
    "blizzard": "Mountain Blizzard & Warm Fireplace • Cozy Winter Timber Cabin [4K]",
    "winter": "Pristine Winter Snowfall • Quiet Evergreen Forest in 4K",
    "autumn": "Golden Autumn River • Crimson Maple Leaves & Cozy Forest Stream [4K]",
    "waterfall_gorge": "Niagara Falls 4K • Calming Waterfall Ambience & Soft Music for Sleep & Focus",
    "waterfall": "Niagara Falls 4K • Calming Waterfall Ambience & Soft Music for Sleep & Focus",
}


def generate_youtube_ambient_package(
    archetype_key: str,
    duration_hours: float = 1.0,
    secondary_element: Optional[str] = None,
    fade_to_black_hours: Optional[float] = None,
) -> YouTubeAmbientPackage:
    """Generate high-CTR YouTube metadata, thumbnail prompt, and chapter timestamps."""
    key = archetype_key.lower().replace("-", "_").replace(" ", "_")
    clean_name = archetype_key.replace("_", " ").title()
    base_title = TITLE_TEMPLATES.get(key, f"{clean_name} 4K • Calming Nature Ambience & Soft Music")

    if secondary_element and "•" in base_title:
        parts = base_title.split("•")
        base_title = f"{parts[0].strip()} with {secondary_element.title()} •{parts[1]}"

    is_30min = (duration_hours <= 0.6)
    if fade_to_black_hours:
        base_title = f"{base_title} • Fades to Black Screen ({int(fade_to_black_hours)}H)"

    # Chapter Markers
    if is_30min:
        chapters = [
            "00:00:00 🌿 Golden Hour Relaxation & Breathwork",
            "00:10:00 🌊 Plunging Cataract Water Wall Focus",
            "00:20:00 🌙 Calming Mist & Peaceful Winddown",
        ]
    else:
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

    dur_label = "30-Minute" if is_30min else f"{int(duration_hours) if duration_hours.is_integer() else duration_hours}-Hour"
    description = (
        f"Immerse yourself in this {dur_label} 4K Velvet Ambient Soundscape featuring {clean_name}.\n\n"
        "✨ Acoustic Engineering: Mastered to -21.0 LUFS with Velvet Low-Pass anti-fatigue filtering "
        "and sub-audible 432Hz delta wave brainwave entrainment to ease insomnia and promote deep restorative sleep.\n\n"
        "⏰ Broadcast Chapters:\n" + "\n".join(chapters) + "\n\n"
        "🎧 For optimal relaxation and sleep, listen with headphones at comfortable volume.\n"
        "🌿 100% Commercial Master Rights | 4K UHD Visuals"
    )

    thumb_prompt = (
        f"High-contrast masterpiece YouTube thumbnail photograph of {clean_name}. "
        "Striking color contrast between warm glowing golden amber light inside and deep atmospheric cool cobalt blue outside. "
        "Extreme visual depth, crisp 35mm optical bokeh, cozy inviting mood, award-winning cinematography, 8k, zero text."
    )

    pinned_comment = (
        "🌿 Welcome to your nightly sanctuary. Leave a comment with one thing you are grateful for today, "
        "put on your headphones, set your sleep timer, and rest deeply. Broadcast chapters are listed in the description. 🌙💤"
    )

    tags = [
        archetype_key, "relaxing_music", "deep_sleep", "432hz", "sleep_meditation",
        "4k_nature", "ambient_soundscape", "asmr", "insomnia_relief"
    ]
    if is_30min:
        tags.extend(["30_minute_relaxation", "30_min_meditation", "power_nap", "study_music", "focus_soundscape"])
    else:
        tags.extend(["all_night_sleep", "fades_to_black_screen"])

    return YouTubeAmbientPackage(
        title=base_title,
        description=description,
        tags=tags,
        thumbnail_prompt=thumb_prompt,
        chapter_markers=chapters,
        pinned_comment=pinned_comment,
    )
