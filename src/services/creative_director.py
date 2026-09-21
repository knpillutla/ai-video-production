"""Autonomous Creative Director Service.

Takes free-form natural language user ideas (e.g. 'good city in europe with colorful
neighborhoods and busy crowded squares') and autonomously expands them into concrete,
cinematic destinations, multi-location hubs, cultural contexts, and production briefs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from src.core.telemetry import logger
from src.mcp.topic_memory.server import check_topic_duplicate, recent_topic_context
from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter


@dataclass
class CreativeBlueprint:
    """Structured production blueprint synthesized by the Creative Director."""
    title: str
    destination_name: str
    country: str
    location_hubs: list[str] = field(default_factory=list)
    format: str = "walking_tour"
    genre: str = "travel_tourism"
    culture: str = "western_global"
    visual_theme: str = ""
    soundtrack_style: str = ""
    foley_cues: str = ""
    pacing_notes: str = ""


_DIRECTOR_SYSTEM_PROMPT = """You are the Lead Creative Director of an elite 4K broadcast video studio (BBC / NatGeo Travel style).
Your mission is to take high-level, vague, or creative user ideas and autonomously develop them into concrete, breathtaking, and culturally authentic world destinations.

Rules:
1. Destination Selection: Autonomously pick a specific, real-world city, village, mountain pass, or cultural landmark matching the user's vibe (e.g. Porto Ribeira, Ghent Medieval Canals, Seville Santa Cruz, Colmar Old Town, Zermatt Matterhorn).
2. Location Hubs (Directive 16): Structure 3 to 4 distinct location hubs for narrative progression (e.g. Hub 1: Riverfront Promenade -> Hub 2: Bustling Food Market -> Hub 3: Historic Belltower Square).
3. Natural Daylight Standard (Directive 13): Outdoor travel/walking tours must default to crisp, open-air natural daylight (5400K-5600K).
4. Audio & Foley: Define authentic local music (e.g. Portuguese Fado guitar, Spanish Flamenco) and procedural foley cues.
5. Strict JSON Output: Return a valid, minified JSON object matching the requested schema without markdown fences or preamble.
"""


async def expand_creative_idea(
    idea: str,
    target_format: str = "walking_tour",
    language: str = "en",
    user_id: str | None = None,
) -> CreativeBlueprint:
    """Expand a vague natural language idea into a fully-formed production blueprint."""
    logger.info(f"creative_director_expanding: idea='{idea}', format={target_format}, lang={language}")
    excluded = recent_topic_context(user_id, language)
    exclusions_text = "; ".join(excluded) if excluded else "none yet"

    if is_mock_mode():
        return CreativeBlueprint(
            title="Vibrant Porto Walking Tour: Historic Ribeira & Bustling Bolhao Market",
            destination_name="Porto (Ribeira & Bolhão)",
            country="Portugal",
            location_hubs=[
                "Praça da Ribeira riverfront promenade with lively outdoor cafes",
                "Mercado do Bolhão bustling market streets with fresh pastry stalls",
                "Clérigos Tower cobblestone alleys with blue azulejo tiled facades",
            ],
            format=target_format,
            genre="travel_tourism",
            culture="portuguese_european",
            visual_theme="Vibrant daytime walking tour along colorful pastel townhouses and sunlit Douro river",
            soundtrack_style="Acoustic Portuguese guitar melody with gentle melodic cadence",
            foley_cues="Cobblestone footsteps, soft river water lapping, lively outdoor cafe murmur",
            pacing_notes="Relaxed 1.8 km/h human walking tour with 15s-20s leisurely scenic glides",
        )

    llm = GeminiLLMAdapter()
    user_prompt = f"""User Idea: "{idea}"
Target Format: {target_format}
Language: {language}
Previously Produced Topics to Exclude: {exclusions_text}

JSON Schema:
{{
  "title": "Concise, highly clickable broadcast title (6-12 words)",
  "destination_name": "Specific City, Region, or Landmark",
  "country": "Country Name",
  "location_hubs": ["Hub 1 description", "Hub 2 description", "Hub 3 description"],
  "format": "{target_format}",
  "genre": "travel_tourism",
  "culture": "Cultural heritage identifier",
  "visual_theme": "Rich visual aesthetic and lighting description (5400K natural daylight)",
  "soundtrack_style": "Authentic regional instrumentation and mood",
  "foley_cues": "Atmospheric physical environmental sound cues",
  "pacing_notes": "Directorial movement and cadence notes"
}}
"""
    for attempt in range(3):
        try:
            raw = await llm.generate_text(
                prompt=user_prompt,
                system_prompt=_DIRECTOR_SYSTEM_PROMPT,
                temperature=0.85,
            )
            clean_json = raw.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            data = json.loads(clean_json.strip())

            blueprint = CreativeBlueprint(
                title=data.get("title", f"{target_format.title()}: {idea[:40]}"),
                destination_name=data.get("destination_name", "Historic Destination"),
                country=data.get("country", "Europe"),
                location_hubs=data.get("location_hubs", [idea]),
                format=data.get("format", target_format),
                genre=data.get("genre", "travel_tourism"),
                culture=data.get("culture", "western_global"),
                visual_theme=data.get("visual_theme", idea),
                soundtrack_style=data.get("soundtrack_style", "Acoustic orchestral travel melody"),
                foley_cues=data.get("foley_cues", "Ambient environmental soundscapes"),
                pacing_notes=data.get("pacing_notes", "Leisurely steadycam glide"),
            )

            # Check topic duplication against memory
            check = await check_topic_duplicate(blueprint.title, metadata={"genre": blueprint.genre, "language": language}, user_id=user_id, language=language)
            if not check.get("is_duplicate"):
                logger.info(f"creative_director_selected: dest='{blueprint.destination_name}', title='{blueprint.title}'")
                return blueprint

            logger.info(f"creative_director_duplicate_detected: '{blueprint.title}', retrying with fresh location...")
        except Exception as e:
            logger.warning(f"creative_director_attempt_failed: {e}")

    # Fallback default if LLM retries fail
    return CreativeBlueprint(
        title=f"Scenic Walking Tour: {idea.title()[:50]}",
        destination_name=idea[:30],
        country="Europe",
        location_hubs=[idea],
        format=target_format,
        visual_theme=idea,
    )


__all__ = ["CreativeBlueprint", "expand_creative_idea"]
