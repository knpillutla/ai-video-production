"""Living Art & Museum Studio Directorial Prompt Engineering.

Specialized in 4K living impressionist oil paintings, grand museum galleries, and Parisian ateliers.
Conforms strictly to the global RelaxScreenplay schema contract.
"""
from __future__ import annotations
from typing import Optional
from src.studios.base_directorial_prompt import build_base_directorial_prompt

ART_LANDMARK_POOL = [
    "Musée d'Orsay Impressionist Gallery, Paris, France",
    "The Louvre Grand Gallery & Classical Salons, Paris, France",
    "Uffizi Gallery Renaissance Corridors, Florence, Italy",
    "Rijksmuseum Honor Gallery, Amsterdam, Netherlands",
    "Claude Monet's Garden & Water Lily Pond at Giverny, France",
    "Montmartre Bohemian Painter Atelier Loft, Paris, France",
    "Kyoto National Museum & Traditional Japanese Tea Atelier, Japan",
    "Sainte-Chapelle Stained Glass Sanctuary, Paris, France",
]

ART_SPECIFIC_RULES = """
======================================================================
LIVING ART & GALLERY STUDIO DIRECTORIAL RULES & CINEMATOGRAPHY:
======================================================================
1. TACTILE ARTISTIC TEXTURES & FRAMING:
   - Frame 16:9 compositions on locked tripod or ultra-slow gallery glide.
   - Capture rich physical art textures: heavy oil impasto peaks, genuine linen canvas weave, cracked oil glazes, 24K hammered gold foil, and carved gilded frames.
   - Purity Guard: Strictly mandate zero tourists, zero smartphones, zero barriers, zero modern clutter.

2. AUTHENTIC MUSEUM LIGHTING STANDARDS:
   - Museum Galleries: High-CRI 3200K warm directional spotlighting with soft falloff.
   - Artist Ateliers: Crisp 5400K natural northern skylight streaming through studio windows.
   - Stained Glass: Brilliant 5600K prismatic jewel-toned sunbeams.

3. LIVING ART CINEMAGRAPH KINETICS:
   - The picture frames, canvas cloth, easels, and gallery walls remain 100% rigid, frozen, and temporally stable.
   - Animate ONLY subtle micro kinetics: gentle ripples across painted water surfaces, sunbeams illuminating dancing dust motes, or faint mist ribbons.
   - Domain: "landscape_solid".

4. ACOUSTIC HARMONICS (432Hz / 528Hz):
   - Pair impressionist scenes with delicate harp, classical cello drone, or Debussy piano harmonics.
   - Pair grand galleries with warm nylon guitar and peaceful hall resonance.
   - Format all audio tags to 48,000 Hz, -14 LUFS broadcast normalization.
"""


def build_art_prompt(
    custom_prompt: str,
    duration_seconds: float,
    num_shots: int,
    archetype: str = "living_impressionism",
    camera_motion: str = "locked_tripod",
    excluded_topics: Optional[list[str]] = None,
    channel_id: Optional[str] = None,
) -> str:
    """Build dedicated Art studio directorial prompt conforming to RelaxScreenplay schema."""
    arch_lower = archetype.lower()

    if "gallery" in arch_lower or "louvre" in arch_lower:
        color_temp = 3200
        cluster = "Grand Nocturne Gallery"
        default_topic = "Grand European art museum gallery at peaceful twilight, parquet floors, gilded frames, and classical marble sculptures"
    elif "atelier" in arch_lower or "studio" in arch_lower or "paris" in arch_lower:
        color_temp = 5400
        cluster = "Sunlit Artist Atelier"
        default_topic = "Sun-drenched Parisian artist atelier loft, tall windows, wooden easels, paint palettes, and drying oil canvases"
    elif "sumie" in arch_lower or "ukiyoe" in arch_lower or "woodblock" in arch_lower:
        color_temp = 5500
        cluster = "Japanese Living Woodblock"
        default_topic = "Living Japanese woodblock print with gentle rolling waves, sumi ink mountains, and handmade washi paper textures"
    elif "stained" in arch_lower or "glass" in arch_lower or "cathedral" in arch_lower:
        color_temp = 5600
        cluster = "Cathedral Stained Glass"
        default_topic = "Monumental Gothic cathedral rose stained glass casting kaleidoscopic jewel-toned sunlight across ancient stone floors"
    elif "klimt" in arch_lower or "gold" in arch_lower:
        color_temp = 3000
        cluster = "Art Nouveau Gold Leaf"
        default_topic = "Art Nouveau living canvas with hammered 24K gold leaf patterns and undulating metallic bronze and marble pigments"
    elif "surreal" in arch_lower or "dream" in arch_lower:
        color_temp = 4200
        cluster = "Surrealist Dreamscape"
        default_topic = "Ethereal surrealist dreamscape with floating stone arches over mirror-still twilight sea under twin crescent moons"
    else:
        color_temp = 5200
        cluster = "Living Impressionist Canvas"
        default_topic = "Living impressionist oil painting with heavy impasto brushstrokes, rippling water lilies, and Claude Debussy piano score"

    return build_base_directorial_prompt(
        genre="relax/art",
        sub_genre=archetype,
        archetype=archetype,
        cluster=cluster,
        custom_prompt=custom_prompt or default_topic,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=excluded_topics,
        specific_rules=ART_SPECIFIC_RULES,
        curation_landmarks=ART_LANDMARK_POOL,
        color_temp_kelvin=color_temp,
        channel_id=channel_id or "earth_serenade",
    )
