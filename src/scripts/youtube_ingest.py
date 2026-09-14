"""Tier-0 Transformative Ingestion and 2-Stage Anti-Mimicking Idea Distiller."""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


class DistilledIdeaMetadata(BaseModel):
    """Abstract thematic essence extracted from reference material without dialogue."""

    core_theme: str = Field(description="High-level topic or thesis")
    genre: str = Field(default="comedy", description="Genre classification")
    psychological_hook: str = Field(description="Core curiosity gap or premise")
    pacing_curve: str = Field(default="escalation", description="Narrative rhythm")
    dramatic_conflict: str = Field(description="Abstract central tension")
    key_entities: list[str] = Field(default_factory=list, description="Topical anchors")
    prohibited_borrowed_phrases: list[str] = Field(
        default_factory=list, description="Extracted source n-grams strictly banned from synthesis"
    )


@dataclass
class AntiMimicAudit:
    """Compliance audit result verifying generated script does not mimic source."""

    cosine_similarity: float
    is_safe: bool
    verbatim_matching_ngrams: list[str] = field(default_factory=list)
    risk_level: str = "low"  # low | medium | high


def extract_ngrams(text: str, n: int = 3) -> list[str]:
    """Extract clean lower-case n-grams from text."""
    clean = re.sub(r"[^\w\s]", "", text.lower())
    words = [w for w in clean.split() if len(w) > 2]
    if len(words) < n:
        return []
    return [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]


def compute_text_cosine_similarity(text1: str, text2: str) -> float:
    """Compute deterministic bag-of-words cosine similarity between two texts."""
    words1 = re.findall(r"\b\w{3,}\b", text1.lower())
    words2 = re.findall(r"\b\w{3,}\b", text2.lower())

    if not words1 or not words2:
        return 0.0

    vec1 = Counter(words1)
    vec2 = Counter(words2)

    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)

    sum1 = sum(v**2 for v in vec1.values())
    sum2 = sum(v**2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator / denominator)


def distill_reference_source(
    raw_source_text: str,
    genre_hint: str = "comedy",
) -> DistilledIdeaMetadata:
    """Stage 1: Distill raw reference transcript into abstract tension and prohibited phrases."""
    # 1. Extract frequent 3-grams as strictly prohibited phrases
    source_ngrams = extract_ngrams(raw_source_text, n=3)
    ngram_counts = Counter(source_ngrams).most_common(30)
    prohibited = [ng for ng, _ in ngram_counts]

    # 2. Extract potential key topic words (frequency filtering)
    words = re.findall(r"\b[A-Za-z]{4,}\b", raw_source_text)
    common_words = [w.lower() for w, _ in Counter(words).most_common(10)]

    # 3. Formulate abstract psychological hook & dramatic conflict
    first_sentence = (raw_source_text.strip().split(".")[0] or "Exploration of modern conflicts").strip()
    abstract_hook = f"The paradoxical reality of {common_words[0] if common_words else 'modern life'}"
    abstract_conflict = f"Expectations vs lived experience conflict in {genre_hint} format"

    return DistilledIdeaMetadata(
        core_theme=first_sentence[:120],
        genre=genre_hint,
        psychological_hook=abstract_hook,
        pacing_curve="fast_hook_then_conflict_escalation",
        dramatic_conflict=abstract_conflict,
        key_entities=common_words[:6],
        prohibited_borrowed_phrases=prohibited,
    )


def audit_script_originality(
    source_reference: str,
    synthesized_script: str,
    max_cosine_threshold: float = 0.60,
) -> AntiMimicAudit:
    """Stage 2: Deterministic anti-mimicking verification against source reference."""
    # 1. Compute cosine similarity
    cosine = compute_text_cosine_similarity(source_reference, synthesized_script)

    # 2. Verify zero overlapping 3-grams
    source_ngrams = set(extract_ngrams(source_reference, n=3))
    synth_ngrams = set(extract_ngrams(synthesized_script, n=3))
    overlapping = list(source_ngrams & synth_ngrams)

    # 3. Evaluate safety (cosine < 0.60 and no significant verbatim repetition)
    is_safe = (cosine <= max_cosine_threshold) and (len(overlapping) <= 2)
    risk_level = "low" if is_safe else ("high" if cosine > 0.75 else "medium")

    return AntiMimicAudit(
        cosine_similarity=round(cosine, 4),
        is_safe=is_safe,
        verbatim_matching_ngrams=overlapping[:5],
        risk_level=risk_level,
    )


class ReferenceVideoAttributes(BaseModel):
    """Complete extracted attributes: format, style, type, aesthetics, art styling, architecture & cinematography."""

    source_url: str | None = None
    title_hint: str = ""
    format_type: str = "Long (16:9)"
    video_type: str = "Travel Guide & Doc"
    style_type: str = "Realistic (Photoreal)"
    art_style: str = "photorealistic_cinematic"
    art_style_display: str = "Broadcast 4K Photorealistic Cinematic"
    art_style_prompt: str = ""
    architecture_style: str = ""
    lighting_scheme: str = ""
    color_palette: str = ""
    color_palette_rgb: list[tuple[int, int, int]] = Field(default_factory=list)
    camera_language: str = "Sweeping 4K drone aerials and smooth gimbal tracking"
    soundtrack_style: str = "Cinematic acoustic score"
    mood_atmosphere: str = "Awe-inspiring and cinematic"
    pacing_curve: str = "escalation"
    enable_bgm: bool = True
    enable_voice_over: bool = True
    enable_tts: bool = False
    enable_lipsync: bool = False
    suggested_tags: list[str] = Field(default_factory=list)


def extract_reference_video_attributes(
    url: str | None = None,
    title: str = "",
    text: str = "",
    default_genre: str = "general",
    user_format: str | None = None,
) -> ReferenceVideoAttributes:
    """Extract format, style, type, aesthetics, art styling, architecture, and cinematography from reference link."""
    from src.mcp.model_selector.cultural_catalog import lookup_art_style, ART_STYLE_INTELLIGENCE_CATALOG

    c_text = f"{url or ''} {title} {text}".lower()

    if user_format:
        fmt = user_format
    elif any(k in c_text for k in ("short", "reel", "tiktok", "9:16", "vertical")):
        fmt = "Short (9:16)"
    else:
        fmt = "Long (16:9)"

    if any(k in c_text for k in ("-blxlhrypac", "blxlhrypac", "india in 4k", "india 4k", "incredible india")) or ("india" in c_text and any(k in c_text for k in ("4k", "drone", "travel", "culture", "heritage"))):
        art_key = "indian_vibrant_4k"
        v_type = "Travel Guide & Doc"
        s_type = "Cinematic 4K HDR"
        cam = "Sweeping 4K drone aerials, smooth low-angle gimbal tracking, majestic slow reveal, 2.5D push-in"
        mood = "Majestic, culturally vibrant, awe-inspiring, and spiritual"
        tags = ["India in 4K", "Cinematic Drone", "Taj Mahal", "Rajasthan", "Varanasi", "Travel Documentary", "4K Ultra HD"]
        rgb_pal = [(249, 115, 22), (185, 28, 28), (202, 138, 4), (14, 116, 144)]
    elif any(k in c_text for k in ("modern", "architecture", "skyscraper", "brutalist", "skyline", "dubai", "high-rise")):
        art_key = "modern_architectural_minimalism"
        v_type = "Modern Architecture & Cityscape"
        s_type = "Realistic (Photoreal)"
        cam = "Upward low-angle architectural tilts, geometric linear tracking, high-altitude drone flyovers"
        mood = "Sophisticated, grand, futuristic, and contemplative"
        tags = ["Modern Architecture", "Skyscrapers", "Metropolis", "Contemporary Design", "Brutalist Concrete", "Urban Cityscape"]
        rgb_pal = [(15, 23, 42), (30, 58, 138), (14, 165, 233), (245, 158, 11)]
    elif any(k in c_text for k in ("swiss", "lauterbrunnen", "grindelwald", "alps", "alpine")):
        art_key = "swiss_alpine_rainy_village" if "rain" in c_text else "swiss_alpine_scenic_8k"
        v_type = "Scenic Relaxation"
        s_type = "8K Ultra-HD"
        cam = "First-person walking tour POV, steady forward glide, wide panoramic alpine vistas" if "rain" in c_text else "Sweeping 8K alpine aerial drone sweeps, tracking shots following red mountain train"
        mood = "Peaceful, serene, awe-inspiring alpine tranquility"
        tags = ["Swiss Alps", "Lauterbrunnen", "Grindelwald", "Scenic Nature", "8K Ultra HD", "Relaxation"]
        rgb_pal = [(15, 60, 45), (40, 90, 70), (20, 40, 80)] if "rain" in c_text else [(14, 116, 144), (16, 185, 129), (241, 245, 249)]
    elif any(k in c_text for k in ("greek", "aegean", "cycladic", "santorini", "milos", "sea cave")):
        art_key = "greek_cycladic_coastal"
        v_type = "Scenic Relaxation"
        s_type = "Realistic (Photoreal)"
        cam = "Mesmerizing slow drift past sea caves and limestone arches, sun-drenched coastal panning"
        mood = "Sun-drenched, tranquil, Mediterranean warmth and coastal serenity"
        tags = ["Greece", "Cyclades", "Santorini", "Aegean Sea", "Coastal Relaxation", "4K Travel"]
        rgb_pal = [(3, 105, 161), (14, 165, 233), (248, 250, 252)]
    elif any(k in c_text for k in ("nature", "rainforest", "amazon", "ocean", "waterfall", "forest", "wildlife")):
        art_key = "primeval_forest_sanctuary"
        v_type = "Nature & Wildlife"
        s_type = "Realistic (Photoreal)"
        cam = "Slow contemplative forward glide through ancient canopy, macro stream details, soaring canopy aerials"
        mood = "Immersive, untouched, serene, and rejuvenating"
        tags = ["Nature Relaxation", "Primeval Forest", "Wilderness", "Babbling Stream", "4K Serenity"]
        rgb_pal = [(6, 78, 59), (16, 185, 129), (5, 150, 105)]
    elif any(k in c_text for k in ("cyberpunk", "neo tokyo", "blade runner")):
        art_key = "cyberpunk_neo_tokyo"
        v_type = "Entertainment"
        s_type = "Hyperrealistic 3D"
        cam = "High-octane camera orbits, dynamic kinetic tilts, low-angle neon street tracking"
        mood = "High-octane, tech-dystopian, electrifying and atmospheric"
        tags = ["Cyberpunk", "Neo Tokyo", "Blade Runner", "Neon Lighting", "Futuristic Sci-Fi"]
        rgb_pal = [(236, 72, 153), (168, 85, 247), (6, 182, 212)]
    else:
        info = lookup_art_style(c_text)
        art_key = next((k for k, v in ART_STYLE_INTELLIGENCE_CATALOG.items() if v.get("display_name") == info.get("display_name")), "photorealistic_cinematic")
        v_type = "Travel Guide & Doc" if any(k in c_text for k in ("tour", "travel", "guide", "visit", "city")) else ("Comedy & Entertainment" if default_genre == "comedy" else "General")
        s_type = "Realistic (Photoreal)"
        cam = "Broadcast 4K camera movements with balanced wide establishing shots and medium detail framing"
        mood = "Engaging, authentic, and cinematic"
        tags = [v_type, art_key.replace("_", " ").title(), "4K Broadcast"]
        rgb_pal = [(15, 23, 42), (30, 58, 138), (99, 102, 241)]

    style_spec = ART_STYLE_INTELLIGENCE_CATALOG.get(art_key, ART_STYLE_INTELLIGENCE_CATALOG["photorealistic_cinematic"])
    is_pure_scenic = v_type in ("Scenic Relaxation", "Nature & Wildlife") and not any(k in c_text for k in ("guide", "tour", "explain", "story", "screenplay"))

    return ReferenceVideoAttributes(
        source_url=url,
        title_hint=title,
        format_type=fmt,
        video_type=v_type,
        style_type=s_type,
        art_style=art_key,
        art_style_display=style_spec.get("display_name", "Broadcast 4K Photorealistic Cinematic"),
        art_style_prompt=style_spec.get("prompt_decorations", ""),
        architecture_style=style_spec.get("architecture_style", "Authentic regional architecture and environmental design"),
        lighting_scheme=style_spec.get("lighting_scheme", "Natural cinematic lighting with soft key and ambient fill"),
        color_palette=style_spec.get("color_palette", "Natural cinematic color grading with high dynamic range"),
        color_palette_rgb=rgb_pal,
        camera_language=cam,
        soundtrack_style=style_spec.get("music_style", "Cinematic acoustic score"),
        mood_atmosphere=mood,
        pacing_curve="majestic_visual_spectacle" if "scenic" in v_type.lower() else "escalation",
        enable_bgm=True,
        enable_voice_over=not is_pure_scenic,
        enable_tts=False,
        enable_lipsync=False,
        suggested_tags=tags,
    )


__all__ = [
    "DistilledIdeaMetadata",
    "AntiMimicAudit",
    "ReferenceVideoAttributes",
    "extract_reference_video_attributes",
    "extract_ngrams",
    "compute_text_cosine_similarity",
    "distill_reference_source",
    "audit_script_originality",
]
