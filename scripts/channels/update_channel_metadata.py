"""Automated YouTube Channel Bio, Description, and SEO Metadata Updater.

Configured for the 3 Flagship Channels of Warm Glow Entertainment:
1. Earth Serenade (@EarthSerenade4K) - 4K Scenic Nature & Earth Sanctuaries
2. Silent Hearth (@SilentHearthSleep) - 8-Hour Deep Sleep & Insomnia Sanctuary
3. Rain & Quill (@RainAndQuill) - 3-Hour Study & Focus Cafe Ambiance
"""

from typing import Dict, List
from pydantic import BaseModel, Field


class ChannelBrandingProfile(BaseModel):
    """Complete branding and SEO configuration for a YouTube channel."""
    channel_name: str
    handle: str
    tagline: str
    about_description: str
    channel_keywords: List[str] = Field(default_factory=list)
    pinned_links: Dict[str, str] = Field(default_factory=dict)


CHANNEL_PROFILES: Dict[str, ChannelBrandingProfile] = {
    "earth_serenade": ChannelBrandingProfile(
        channel_name="Earth Serenade",
        handle="@EarthSerenade4K",
        tagline="Breathtaking 4K Earth Sanctuaries & Cinematic Nature Relaxation",
        about_description=(
            "🌿 Welcome to Earth Serenade — your cinematic escape into the world's most breathtaking natural sanctuaries.\n\n"
            "We produce master-grade 4K 60fps scenic nature documentaries, Swiss Alpine walking tours, sacred mountain ranges, "
            "and crystalline ocean retreats paired with our signature 'Velvet Sound' anti-fatigue acoustic mastering.\n\n"
            "✨ What Makes Earth Serenade Unique:\n"
            "• Native 4K UHD Master Visuals (3840×2160, visually lossless)\n"
            "• -21.0 LUFS Velvet Anti-Fatigue Audio (No harsh treble, zero ear fatigue for 8+ hours)\n"
            "• Multi-perspective cinematography & living biophilic soundscapes\n"
            "• 100% Commercial Master Rights & YPP Safe\n\n"
            "🎧 Perfect for deep relaxation, yoga, meditation, study, and bringing the beauty of nature into your living space.\n\n"
            "✨ Produced with care by Warm Glow Entertainment."
        ),
        channel_keywords=[
            "earth serenade", "nature relaxation 4k", "swiss alps 4k", "relaxing nature",
            "4k scenic video", "meditation nature", "calm ocean waves", "mountain mist",
            "ambient nature", "nature documentary", "4k landscape", "biophilic sounds", "warm glow entertainment"
        ],
    ),
    "silent_hearth": ChannelBrandingProfile(
        channel_name="Silent Hearth",
        handle="@SilentHearthSleep",
        tagline="8-Hour All-Night Sleep, 432Hz Delta Waves & Fireplace Blizzard Ambiance",
        about_description=(
            "🌙 Welcome to Silent Hearth — your nightly shelter for deep, restorative, unbroken sleep.\n\n"
            "If your mind races at bedtime, our 8-hour sleep broadcasts are scientifically engineered to ease insomnia, "
            "featuring Circadian Fade-to-Black OLED screens and 432Hz binaural delta wave (2.0 Hz) brainwave entrainment.\n\n"
            "✨ Silent Hearth Features:\n"
            "• 8-Hour Full Night Sleep Broadcasts with Circadian Fade-to-Black (Screen dims for bedroom TV comfort)\n"
            "• 432Hz / 528Hz Binaural Delta Waves for deep REM sleep induction\n"
            "• De-popped foley (No sudden loud crackles or startling volume spikes)\n"
            "• Soft blizzard mountain cabins, crackling stone fireplaces, and gentle rain\n\n"
            "💤 Put on your headphones, set your sleep timer, and rest easy tonight.\n\n"
            "✨ Produced with care by Warm Glow Entertainment."
        ),
        channel_keywords=[
            "silent hearth", "sleep music", "deep sleep 8 hours", "432hz sleep",
            "black screen rain", "fades to black screen", "insomnia relief", "blizzard fireplace sleep",
            "delta waves sleep", "sleep sounds", "night rain on window", "asmr sleep", "warm glow entertainment"
        ],
    ),
    "rain_and_quill": ChannelBrandingProfile(
        channel_name="Rain & Quill",
        handle="@RainAndQuill",
        tagline="3-Hour Pomodoro Focus Blocks, Rain on Glass & Cozy Ambiance Cafe",
        about_description=(
            "☕ Welcome to Rain & Quill — your cozy aesthetic workspace for deep focus, coding, reading, and study sessions.\n\n"
            "Designed for students, writers, and remote workers, our 3-hour focus blocks combine gentle rain against window glass, "
            "warm upright felt piano melodies, and comforting coffee shop ambiances.\n\n"
            "✨ Rain & Quill Features:\n"
            "• 3-Hour Uninterrupted Focus & Pomodoro Work Blocks\n"
            "• Biophilic Warmth Curve & Soft Rain ASMR (Engineered for ADHD & high concentration)\n"
            "• Cozy beach house rainstorms, library nooks, and steaming coffee vibes\n"
            "• 4K visual aesthetic that creates the ultimate digital workspace\n\n"
            "🎧 Put on your headphones, grab your favorite hot beverage, and let's get to work.\n\n"
            "✨ Produced with care by Warm Glow Entertainment."
        ),
        channel_keywords=[
            "rain and quill", "study ambiance", "rain on window focus", "3 hours study with me",
            "adhd focus music", "cozy coffee shop rain", "beach house storm focus", "felt piano study",
            "deep work ambiance", "cozy library rain", "coding music", "pomodoro background", "warm glow entertainment"
        ],
    ),
}


def get_channel_branding_bundle(channel_key: str) -> ChannelBrandingProfile:
    """Retrieve SEO-optimized branding bundle for a specific channel."""
    clean = channel_key.lower().replace("-", "_").replace(" ", "_")
    return CHANNEL_PROFILES.get(clean, CHANNEL_PROFILES["earth_serenade"])
