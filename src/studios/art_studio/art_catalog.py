"""Living Art & Gallery Studio Archetype Catalog & Audiovisual Metadata."""
from __future__ import annotations
from typing import Any, Dict

ART_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "living_impressionism": {
        "title": "Living Impressionist Canvas & Textured Oil Impasto",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5200,
        "lighting_desc": "Balanced natural gallery daylight highlighting dimensional oil impasto peaks and brush textures",
        "visual_prompt": (
            "Masterpiece 4K macro photograph of a living impressionist oil painting. Heavy textured impasto brushstrokes, "
            "rich oil paint dimensionality, and vivid colors depicting gently rippling water lilies and weeping willows under "
            "Claude Monet inspired brushwork. 16:9 framing, genuine linen canvas weave, museum gallery illumination, zero modern clutter."
        ),
        "motion_prompt": (
            "Ultra-subtle living canvas cinemagraph. The heavy oil impasto peaks, canvas weave, and wooden easel frame remain 100% frozen, "
            "rigid, and temporally stable. Only micro ripples softly glide across the painted water surface. Zero camera movement, zero panning."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[impressionist peace], delicate French acoustic harp, gentle cello drone, impressionistic piano harmonics, soft studio silence, 432Hz, -14 LUFS",
    },
    "grand_gallery": {
        "title": "Louvre & Uffizi Grand Nocturne Gallery Walk",
        "diurnal_timing": "twilight_blue_hour",
        "color_temp_kelvin": 3200,
        "lighting_desc": "Warm directional 3200K museum spotlights illuminating gilded picture frames in a quiet twilight hall",
        "visual_prompt": (
            "Masterpiece 4K photograph looking down a grand, high-ceilinged European art museum gallery at peaceful twilight. "
            "Polished herringbone parquet hardwood floors reflecting warm directional gallery spotlights, gilded ornate picture frames, "
            "and classical marble sculptures in timeless stillness. Hasselblad medium format clarity, 16:9 framing, serene dignified atmosphere."
        ),
        "motion_prompt": (
            "Ultra-slow cinematic museum tracking glide. Polished wooden floors, gilded frames, and classical marble sculptures remain "
            "100% rigid, frozen, and razor-sharp. Faint micro dust motes drift peacefully through warm spotlight cones. Level horizon stabilization."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[museum sanctuary], gentle classical nylon guitar, warm acoustic cello reverb, echoing quiet gallery footsteps, velvet ambient pads, 432Hz, -14 LUFS",
    },
    "artist_atelier": {
        "title": "Sunlit Parisian Artist Atelier Loft & Easels",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5400,
        "lighting_desc": "Crisp 5400K natural northern skylight streaming through tall studio glass windows",
        "visual_prompt": (
            "Masterpiece 4K photograph inside a sun-drenched bohemian Parisian artist atelier loft. Large industrial iron glass windows "
            "overlook Paris zinc rooftops as soft morning sunlight illuminates weathered wooden easels, turpentine bottles, jars of camel-hair brushes, "
            "and drying textured oil canvases. 16:9 framing, warm cedar wood and oil paint textures, pure creative solitude."
        ),
        "motion_prompt": (
            "Ultra-subtle living studio cinemagraph. Wooden easels, drying canvases, and palette tables remain 100% stationary and temporally stable. "
            "Soft sunbeams slowly illuminate ambient dust motes dancing in the air. Zero camera jitter, zero panning."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[atelier morning], Parisian acoustic accordion harmonics, gentle classical guitar, light rain tapping on studio skylight glass, peaceful warmth, 432Hz, -14 LUFS",
    },
    "sumie_ukiyoe": {
        "title": "Japanese Ukiyo-e Woodblock & Sumi-e Ink Wash",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5500,
        "lighting_desc": "Clean natural daylight revealing delicate handmade washi paper textures and deep charcoal ink gradients",
        "visual_prompt": (
            "Masterpiece 4K living art photograph inspired by Japanese Edo-period woodblock prints and monochrome sumi-e ink washes. "
            "Textured handmade washi paper grain, delicate black sumi ink mountain silhouettes, and stylized rolling waves reminiscent of Hokusai, "
            "framed with weathered natural cedar wood. Symmetrical 16:9 composition, authentic Japanese artistic serenity."
        ),
        "motion_prompt": (
            "Subtle living woodblock cinemagraph. Handcrafted washi paper and mountain silhouettes remain rigid and temporally stable. "
            "Gentle stylized foam ripples glide along the crest of the painted waves. Zero jitter, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[zen ink], traditional Japanese koto resonance, airy shakuhachi flute, resonant temple bells, gentle bamboo fountain drip, 432Hz, -14 LUFS",
    },
    "stained_glass": {
        "title": "Cathedral Rose Stained Glass & Kaleidoscopic Light",
        "diurnal_timing": "daytime",
        "color_temp_kelvin": 5600,
        "lighting_desc": "Brilliant midday sunlight casting vibrant kaleidoscopic jewel-toned shadows across ancient stonework",
        "visual_prompt": (
            "Masterpiece 4K photograph inside a monumental Gothic cathedral sanctuary. Colossal stained glass rose window ablaze with "
            "jewel-toned sapphire, ruby, and amber glass, casting radiant beams of kaleidoscopic prismatic light across ancient carved stone "
            "pillars and flagstones. Arri Alexa 65 cinematography, 16:9 framing, sacred awe and profound stillness."
        ),
        "motion_prompt": (
            "Ethereal sacred light cinemagraph. Gothic stone arches, pillars, and leaded glass window tracery remain 100% rigid and razor-sharp. "
            "Jewel-toned sunbeams gently shimmer across the stone floor with rising incense wisps. Zero camera movement."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[sacred light], ethereal choral ambient pad, resonant cathedral pipe organ whisper, 528Hz Solfeggio harmonic serenity, deep peace, -14 LUFS",
    },
    "klimt_gold_leaf": {
        "title": "Art Nouveau Gold Leaf & Undulating Marble Pigments",
        "diurnal_timing": "golden_hour",
        "color_temp_kelvin": 3000,
        "lighting_desc": "Warm 3000K golden illumination making hammered 24K gold foil and metallic pigments glow richly",
        "visual_prompt": (
            "Masterpiece 4K photograph of an Art Nouveau living tapestry inspired by Gustav Klimt. Intricate hammered 24K gold leaf "
            "geometric patterns, iridescent mother-of-pearl inlays, and swirling metallic bronze and emerald marble pigments. "
            "Cinematic 16:9 composition on locked tripod, luxurious organic patterns, mesmerizing craftsmanship."
        ),
        "motion_prompt": (
            "Hypnotic metallic living wallpaper. The intricate gold leaf filigree remains rigid and razor-sharp. Subtle micro specular glints "
            "dance across the metallic bronze and gold textures. Zero camera jitter, zero morphing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[golden peace], warm neo-classical acoustic piano, rich cello harmony, subtle velvet ambient synth, relaxing restorative sleep, 432Hz, -14 LUFS",
    },
    "surrealist_dream": {
        "title": "Surrealist Dreamscape & Floating Celestial Sanctuaries",
        "diurnal_timing": "twilight_night",
        "color_temp_kelvin": 4200,
        "lighting_desc": "Dreamlike ethereal starlight and twin crescent moons casting silvery reflections across floating stone arches",
        "visual_prompt": (
            "Masterpiece 4K ethereal surrealist artwork inspired by Salvador Dali and celestial dreamscapes. Floating stone arches hover "
            "serenely over a mirror-still twilight sea under two crescent moons and glowing celestial nebula clouds. "
            "Cinematic 16:9 panoramic perspective, hypnotic dreamlike scale, immaculate surrealist beauty."
        ),
        "motion_prompt": (
            "Ethereal dream cinemagraph. Floating stone arches and distant crystal peaks remain frozen and rigid. Gentle celestial nebula "
            "mist slowly drifts across the starlit sky. Completely stationary locked tripod framing."
        ),
        "domain": "landscape_solid",
        "audio_tags": "[deep dream], expansive celestial synthesizer pads, singing Tibetan crystal bowls, warm acoustic cello drone, deep sleep frequency, 432Hz, -14 LUFS",
    },
}


def get_art_archetype(key: str) -> Dict[str, Any]:
    """Retrieve art archetype by key with graceful fallback."""
    k = key.lower()
    for arch_key, data in ART_ARCHETYPES.items():
        if arch_key in k or k in arch_key:
            return data
    return ART_ARCHETYPES["living_impressionism"]


def get_all_art_archetypes() -> list[Dict[str, Any]]:
    """Return all art archetypes as a list of dicts."""
    return [{"id": k, **v} for k, v in ART_ARCHETYPES.items()]
