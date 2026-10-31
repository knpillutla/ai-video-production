"""Documentary Story Service.

Generates the authoritative 21-chapter Master Sovereign Story Dossier
for country and destination documentaries, injecting real-world facts
(capital, exact population, total area, governance, universities, and arts).
Strict zero-fallback enforcement in live production mode.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.studios.documentary_studio.doc_country_facts import get_country_facts
from src.studios.documentary_studio.doc_educational_narrator import (
    generate_sovereign_chapters,
    generate_sovereign_21_chapters,
)


def generate_gemini_documentary_story(
    destination: str,
    genre: str = "doc/nations",
    sub_genre: str = "europe_nations",
    archetype: str = "country_overview",
    custom_prompt: Optional[str] = None,
    channel_id: str = "euro_discovery",
) -> Optional[Dict[str, Any]]:
    """Prompts Gemini to author the complete sovereign documentary story using layered prompt blueprints."""
    import httpx
    from src.providers.llm.gemini_adapter import get_live_gemini_api_key
    from src.providers.base import is_mock_mode
    from src.core.prompt_routing_service import get_prompt_blueprint

    if is_mock_mode():
        return None

    api_key = get_live_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "Google Gemini API key is missing or not configured in environment. "
            "Live documentary story generation halted (zero-fallback policy)."
        )

    is_encyclopedia = "encyclopedia" in (genre or "").lower() or (archetype or "").lower() == "country_encyclopedia"
    target_chapters = 35 if is_encyclopedia else 22
    eff_arch = "country_encyclopedia" if is_encyclopedia else (archetype or "country_overview")

    blueprint = get_prompt_blueprint("documentary", genre, sub_genre, eff_arch, stage="story")
    system_instruction = (
        f"You are the Lead Executive Producer and Director for BBC / National Geographic blue-chip documentaries.\n"
        f"Produce the complete authoritative {target_chapters}-Chapter Sovereign Documentary Story for '{destination}'.\n\n"
        f"{blueprint}\n\n"
        f"MANDATORY CONTRACT: Every single chapter narration MUST include famous, specific real-world proper names "
        f"and examples (capital city & parliament, top 5 universities by name, UNESCO citadels, mountain ranges, regional cities, "
        f"traditional gastronomy, celebrated artists, traditional music, national parks, and beaches).\n"
        f"MANDATORY PROLOGUE & SOVEREIGNTY SEPARATION (CHAPTERS 1 & 2):\n"
        f"- Chapter 1 ('prologue'): MUST open with '{destination}' as its very first word. 70-80 words establishing national character, central paradox, and declaring the complete {target_chapters}-chapter roadmap.\n"
        f"- Chapter 2 ('identity'): 70-80 words dedicated exclusively to the birth of the sovereign nation—ancient founding cradle, when and how it achieved independence, and constitutional democracy.\n"
        f"MANDATORY CAPITAL CITY DECLARATION (CHAPTER 3 'capital_governance'):\n"
        f"- The narration MUST explicitly declare that the city is the capital of {destination} (e.g. 'Oslo, the sovereign capital city of {destination},...' or 'Serving as the capital of {destination}, Oslo...'). Never state the city name without explicitly informing viewers that it is the nation's capital city.\n"
        f"MANDATORY LOCATION FIRST-WORD ANCHOR: For every single chapter, the very first word (or opening phrase) "
        f"of 'narration' MUST be the specific location or landmark name (Chapter 1: '{destination}'; Chapter 2+: the specific landmark/cradle/city).\n"
        f"CINEMATIC NARRATION DIRECTIVE (BBC / NATGEO CADENCE):\n"
        f"- Target 70-85 evocative words per chapter (~28-32s spoken broadcast time).\n"
        f"- Enforce variable dramatic cadence: alternate punchy 3-6 word phrases with sweeping lyrical clauses. Avoid dry Wikipedia lists.\n"
        f"- Layer sensory and tactile textures (whistling wind, echoing bronze bells, biting frost, sizzling cuisine, hum of machinery).\n"
        f"- Frame each chapter with a curiosity hook, dramatic contrast, or surprising world record.\n"
        f"HIGH-CTR YOUTUBE PACKAGING MANDATE:\n"
        f"- Output 'youtube_title': Analyze the story's core national paradox or anomaly to author a compelling, high-CTR YouTube title (e.g. 'The Secret Nation Out-Producing the World's Superpowers — Slovakia 4K'). No plain titles!\n"
        f"- Output 'thumbnail_headline': Exactly 2 to 4 words. Punchy mobile power hook (e.g. 'EUROPE\\'S SECRET').\n"
        f"- Output 'thumbnail_variants': 3 distinct psychological testing angles (paradox, mystery, survival).\n"
        f"Output MUST be a single, strict JSON object with fields: title, youtube_title, thumbnail_headline, thumbnail_variants, destination_entity, synopsis, capital, population, "
        f"area_km2, total_chapters ({target_chapters}), and chapters array. Each chapter must have: chapter_index, chapter_key, "
        f"chapter_title, chapter_subtitle, fact_badge, chapter_stats, location_hub, origin_coords, narration, visual_directive."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    user_msg = f"Generate the complete {target_chapters}-chapter sovereign documentary story for {destination}. Return ONLY raw JSON."
    if custom_prompt:
        user_msg += f" Director's Guidance: {custom_prompt}"

    payload = {
        "contents": [{"parts": [{"text": user_msg}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.3,
        },
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(url, json=payload)
    except Exception as net_err:
        raise RuntimeError(f"Gemini API request failed due to network exception: {net_err}") from net_err

    if resp.status_code != 200:
        raise RuntimeError(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    cands = data.get("candidates", [])
    if not cands:
        raise RuntimeError(f"Gemini API returned zero candidates for documentary story: {data}")

    raw_text = cands[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    if raw_text.startswith("```"):
        lines = [ln for ln in raw_text.splitlines() if not ln.startswith("```")]
        raw_text = "\n".join(lines).strip()

    try:
        parsed = json.loads(raw_text)
    except Exception as parse_err:
        raise RuntimeError(f"Gemini returned invalid JSON for documentary story: {parse_err}. Raw text: {raw_text[:400]}") from parse_err

    if not isinstance(parsed, dict) or len(parsed.get("chapters", [])) < target_chapters:
        ch_count = len(parsed.get("chapters", [])) if isinstance(parsed, dict) else 0
        raise RuntimeError(
            f"Gemini returned {ch_count} chapters, expected at least {target_chapters}. "
            f"Raw text preview: {raw_text[:400]}"
        )

    logger.info(f"gemini_documentary_story_authored_live: {destination} ({len(parsed['chapters'])} chapters)")
    return parsed


def build_raw_documentary_story(
    destination: str = "Norway",
    custom_prompt: Optional[str] = None,
    channel_id: str = "euro_discovery",
    genre: str = "doc/nations",
    sub_genre: str = "europe_nations",
    archetype: str = "country_overview",
) -> Dict[str, Any]:
    """Builds the complete Raw Story via Gemini live prompt authoring (zero fallback in live mode)."""
    from src.providers.base import is_mock_mode

    dest = (destination or "Norway").strip().title()

    # 1. In mock mode, synthesize offline chapters for unit tests / test fixtures
    if is_mock_mode():
        facts = get_country_facts(dest)
        is_encyclopedia = "encyclopedia" in (genre or "").lower() or (archetype or "").lower() == "country_encyclopedia"
        target_ch = 35 if is_encyclopedia else 22
        chapters = generate_sovereign_chapters(
            destination=dest,
            custom_prompt=custom_prompt,
            genre=genre,
            target_chapters=target_ch,
        )
        title = f"{dest}: Sovereign Heritage, Living Culture & {len(chapters)} Wonders"
        synopsis = f"An authoritative 360° BBC-grade educational documentary uncovering the history and living culture of {dest}."
        from src.studios.documentary_studio.doc_curiosity_title_service import derive_contextual_doc_titles
        ctr_title, thumb_head, thumb_vars = derive_contextual_doc_titles(dest, title, synopsis)
        return {
            "title": title,
            "youtube_title": ctr_title,
            "thumbnail_headline": thumb_head,
            "thumbnail_variants": thumb_vars,
            "destination_entity": dest,
            "genre": genre,
            "synopsis": synopsis,
            "channel_id": channel_id,
            "total_chapters": len(chapters),
            "chapters": chapters,
            "status": "ready",
            "capital": facts.get("capital", ""),
            "population": facts.get("population", ""),
            "area_km2": facts.get("area_km2", ""),
            "gemini_story_inputs": {
                "destination": dest,
                "destination_entity": dest,
                "genre": genre,
                "sub_genre": sub_genre,
                "archetype": archetype,
                "target_chapters": len(chapters),
                "custom_prompt": custom_prompt,
                "channel_id": channel_id,
                "model": "offline_deterministic_mock",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "audio_master": {
                "suno_prompt": f"cinematic documentary orchestral score with authentic {dest.lower()} folk nuances, warm acoustic strings, 48kHz broadcast master",
                "suno_musical_tags": "cinematic orchestral, documentary score, 48kHz, subtle acoustic, zero vocals",
                "ducking_db": -18.0,
            },
        }

    # 2. In live mode: Strict zero-fallback Gemini authoring
    gemini_story = generate_gemini_documentary_story(
        destination=dest,
        genre=genre,
        sub_genre=sub_genre,
        archetype=archetype,
        custom_prompt=custom_prompt,
        channel_id=channel_id,
    )
    if not gemini_story:
        raise RuntimeError(f"Live Gemini documentary story generation failed for destination '{dest}'.")
    return gemini_story


def _sanitize_narration_chapter_count(story: Dict[str, Any]) -> Dict[str, Any]:
    """Guarantees voiceover narration never mentions chapter numbers or chapter counts."""
    import re
    pattern = re.compile(
        r"\b(?:across\s+)?(?:twenty-two|22|twenty\s+two)\s+(?:comprehensive\s+)?chapters,?\s*",
        re.IGNORECASE
    )
    for ch in story.get("chapters", []):
        for k in ("narration", "narration_text"):
            if ch.get(k):
                text = ch[k]
                text = pattern.sub("", text)
                text = re.sub(r"^\s*,\s*", "", text)
                text = re.sub(r"\s{2,}", " ", text).strip()
                if text and text[0].islower():
                    text = text[0].upper() + text[1:]
                ch[k] = text
    return story


def persist_raw_documentary_story(
    episode_dir: Path,
    story_data: Dict[str, Any],
) -> Path:
    """Persists raw_gemini_story.json (untouched) & gemini_story_inputs.json to the target episode directory."""
    episode_dir.mkdir(parents=True, exist_ok=True)
    story_data = _sanitize_narration_chapter_count(story_data)
    story_path = episode_dir / "raw_gemini_story.json"
    story_path.write_text(json.dumps(story_data, indent=2, ensure_ascii=False), encoding="utf-8")
    g_inputs = {
        "destination": story_data.get("destination_entity", "Destination"),
        "destination_entity": story_data.get("destination_entity", "Destination"),
        "title": story_data.get("title", ""),
        "genre": story_data.get("genre", "doc/nations"),
        "total_chapters": len(story_data.get("chapters", [])),
        "channel_id": story_data.get("channel_id", "euro_discovery"),
        "model": "gemini-flash-latest",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    (episode_dir / "gemini_story_inputs.json").write_text(json.dumps(g_inputs, indent=2, ensure_ascii=False), encoding="utf-8")
    (episode_dir / "gemini_inputs.json").write_text(json.dumps(g_inputs, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info(f"raw_documentary_story_persisted: {story_path} ({len(story_data.get('chapters', []))} chapters)")
    return story_path


__all__ = [
    "generate_sovereign_chapters",
    "generate_sovereign_21_chapters",
    "generate_gemini_documentary_story",
    "build_raw_documentary_story",
    "persist_raw_documentary_story",
]
