"""Documentary High-CTR Curiosity Title & Thumbnail Hook Derivation.

Derives country-specific, high-voltage YouTube titles and 2-to-4 word thumbnail headlines
from the country's unique cultural context, epithet, and story beats.
Rotates dynamically across 5 distinct psychological title formulas to prevent repetitive phrasing.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

_GENERIC_STOP_WORDS = {
    "travel", "guide", "overview", "documentary", "exploration", "places", "cities",
    "vacation", "tourism", "destination", "standalone", "profile", "encyclopedia",
    "events", "trip", "tour", "video", "4k", "uhd",
}

_MINOR_WORDS = {"of", "the", "and", "in", "for", "on", "at", "to", "a", "an"}


def _title_case_clean(s: str) -> str:
    """Formats title case preserving lowercase minor prepositions and conjunctions."""
    words = s.split()
    if not words:
        return ""
    res = [words[0].capitalize()]
    for w in words[1:]:
        res.append(w.lower() if w.lower() in _MINOR_WORDS else w.capitalize())
    return " ".join(res)


def _clean_epithet(text: str, dest: str) -> str:
    """Extracts clean evocative epithet from a title or synopsis."""
    if not text:
        return ""
    clean = re.sub(rf"^\s*{re.escape(dest)}\s*[:\-–—]\s*", "", text, flags=re.IGNORECASE).strip()
    clean = re.sub(r"\[.*?\]|\(.*?\)", "", clean).strip()
    words = [w for w in clean.split() if w.lower() not in _GENERIC_STOP_WORDS]
    if len(words) < 2:
        return ""
    return _title_case_clean(" ".join(words))


def _condense_thumbnail_hook(text: str, dest: str) -> str:
    """Condenses text into a high-impact 2 to 4 word thumbnail headline."""
    if not text:
        return f"THE REAL {dest.upper()}"
    clean = re.sub(rf"\b(what is|best known for|who was|why did|in this place)\b", "", text, flags=re.IGNORECASE).strip()
    words = [w.upper() for w in clean.split() if w.lower() not in _GENERIC_STOP_WORDS and len(w) > 1]
    if not words or len(words) < 2:
        return f"THE REAL {dest.upper()}"
    if len(words) > 4:
        words = words[:3]
    return " ".join(words)


def _format_rotating_title(dest: str, epithet: str, seed_num: int) -> str:
    """Selects from 5 distinct BBC/NatGeo documentary title formulas based on seed to ensure channel diversity."""
    if epithet and len(epithet.split()) >= 2:
        formulas = [
            f"{epithet}: Inside {dest}'s 21 Sovereign Wonders | 4K UHD",
            f"The Complete Expedition Across {dest}: {epithet} | 4K Documentary",
            f"{epithet}: The Untold Story of {dest} | 4K Documentary",
            f"{epithet}: The Living Story of {dest} | 4K Documentary",
            f"{epithet}: How {dest} Forged a Modern Republic | 4K UHD",
        ]
    else:
        formulas = [
            f"The Complete Expedition Across {dest}: 21 Sovereign Wonders | 4K UHD",
            f"Inside {dest}: Europe's Most Underrated Nation | 4K Documentary",
            f"The Untold Story of {dest}: 21 Sovereign Wonders | 4K Documentary",
            f"The Living Story of {dest}: From Ancient Bastions to Modern Horizons | 4K",
            f"Discovering {dest}: The 360° Sovereign Documentary | 4K UHD",
        ]
    return formulas[seed_num % len(formulas)]


def derive_contextual_doc_titles(
    destination: str,
    raw_title: Optional[str] = None,
    synopsis: Optional[str] = None,
    episode_index: int = 1,
    gemini_yt_title: Optional[str] = None,
    gemini_thumb_headline: Optional[str] = None,
    gemini_thumb_variants: Optional[List[Dict[str, str]]] = None,
) -> Tuple[str, str, List[Dict[str, str]]]:
    """Derives context-matched high-CTR YouTube title, 2-4 word thumbnail hook, and A/B variants.

    Prioritizes Gemini's dynamically authored paradox title & thumbnail hook from the story.
    Falls back to deterministic formula selection when in offline test mode.
    """
    dest = (destination or "Europe").strip().title()

    # 1. Primary Authority: Gemini Dynamic YouTube Title
    if gemini_yt_title and len(gemini_yt_title.strip()) > 15 and not any(w in gemini_yt_title.lower() for w in ["none", "standalone", "untitled"]):
        ctr_title = gemini_yt_title.strip()
    else:
        epithet = _clean_epithet(raw_title or "", dest)
        if not epithet and synopsis:
            m = re.search(r"exploring\s+(?:the\s+)?([^,.]+)", synopsis, re.IGNORECASE)
            if m:
                epithet = _clean_epithet(m.group(1), dest)
        dest_seed = sum(ord(c) for c in dest) + int(episode_index or 1)
        ctr_title = _format_rotating_title(dest, epithet, dest_seed)

    # 2. Primary Authority: Gemini Dynamic Thumbnail Headline (2 to 4 words)
    if gemini_thumb_headline and 2 <= len(gemini_thumb_headline.strip().split()) <= 4:
        primary_thumb = gemini_thumb_headline.strip().upper()
    else:
        epithet = _clean_epithet(raw_title or "", dest)
        if epithet and 2 <= len(epithet.split()) <= 4:
            primary_thumb = epithet.upper()
        else:
            primary_thumb = _condense_thumbnail_hook(raw_title or epithet, dest)

    # 3. Dynamic A/B/C Thumbnail Variants
    if gemini_thumb_variants and len(gemini_thumb_variants) >= 2:
        variants = gemini_thumb_variants
    else:
        variants = [
            {"variant": "A", "headline": primary_thumb, "angle": "poetic_epithet"},
            {"variant": "B", "headline": f"{dest.upper()}'S SECRET", "angle": "hidden_anomaly"},
            {"variant": "C", "headline": f"HOW {dest.upper()} SURVIVED", "angle": "scale_paradox"},
        ]

    return ctr_title, primary_thumb, variants


__all__ = ["derive_contextual_doc_titles"]
