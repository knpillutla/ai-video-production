"""Autonomous Creative Variation & Topic Diversification Planner.

Generates distinct, non-repeating premises across cities, villages, mountains,
and cultural attractions, strictly enforcing persistent Topic Memory exclusions.
"""

from uuid import uuid4

from src.core.telemetry import logger
from src.mcp.topic_memory.server import check_topic_duplicate, recent_topic_context
from src.providers.base import is_mock_mode
from src.providers.llm.gemini_adapter import GeminiLLMAdapter


def build_variation_prompt(brief: str, language: str, excluded: list[str]) -> str:
    """Construct a creative variation prompt instructing Gemini to pick concrete, diverse locations."""
    exclusions = "; ".join(excluded) if excluded else "none yet"
    return (
        "Return only one concise episode premise, 6-14 words, with no label or punctuation. "
        "You are planning the next distinct production in a recurring series. "
        f"Creative brief: {brief}. Return the canonical title in English, even when the production language is {language}. "
        "Choose a materially different setting, subject, narrative hook, and cultural angle from prior episodes. "
        "Autonomously pick a specific, concrete world location, city, village, mountain, or landmark attraction: "
        "- For walking tours / travel: vary real destinations and trails (e.g. for Norway: Geirangerfjord cliffside trail, "
        "Lofoten Islands Reinebringen ridge, Bergen Bryggen cobblestone wharf, Preikestolen Pulpit Rock, Flåm valley waterfall trek; "
        "for Switzerland: Zermatt Matterhorn trail, Lauterbrunnen valley, Grindelwald First; these are examples, never a fixed rotation). "
        "- For tourist attractions / city guides: vary iconic sights, neighborhoods, viewpoints, and districts (e.g. for New York: Brooklyn Bridge promenade, Central Park Bethesda Terrace, Top of the Rock, Greenwich Village; for Paris: Montmartre Sacré-Cœur, Louvre courtyard, Seine riverbanks). "
        "- For movies / historical epics / fantasy: vary dramatic conflict hooks, historic kingdoms, battlefields, or mythical realms (e.g. 13th-century Scottish citadel siege, fortress intrigue, ancient forest clash). "
        "- For dance / cultural music videos: vary authentic festive celebrations, village jatharas, regional festival streets, and temple courtyards (e.g. for Telugu: Medaram Sammakka Sarakka Jathara, Sankranthi harvest festival village, Bonalu procession in Old Hyderabad, Godavari Lanka coconut grove festival, Tirupati Gangamma Jathara, Rayalaseema rustic fair; vary choreographic hook step concepts and festive themes; never repeat prior settings). "
        "CRITICAL LIGHTING DIRECTIVE (Directive 13): All outdoor walking tours, travel guides, and nature productions MUST strictly default to crisp, open-air natural daylight (5400K-5600K). Never choose twilight, dusk, night, dawn, or blue hour unless explicitly requested in the brief. "
        f"Do not repeat or closely paraphrase these prior premises: {exclusions}."
    )


async def get_fresh_original_topic(
    theme: str,
    show_slug: str = "default",
    language: str = "en",
    user_id: str | None = None,
) -> str:
    """Ask Gemini for a novel premise and verify it against persistent topic memory with automatic exclusion."""
    excluded = recent_topic_context(user_id, language)
    planner = GeminiLLMAdapter()
    dup_meta = {"genre": theme, "show_slug": show_slug, "language": language}

    for attempt in range(3):
        if is_mock_mode():
            candidate = f"{theme.title()} original variation {uuid4().hex[:8]}"
        else:
            candidate = await planner.generate_text(
                build_variation_prompt(theme, language, excluded),
                system_prompt="You are a concise creative-variation and location planner.",
                temperature=0.9,
            )
            candidate = candidate.strip().splitlines()[0].strip(" #-:.")[:140]

        check = await check_topic_duplicate(
            candidate, metadata=dup_meta,
            user_id=user_id, language=language,
        )
        if not check.get("is_duplicate", False):
            logger.info(f"topic_planner_fresh_topic_found: topic='{candidate}' similarity={check.get('max_similarity_score', 0)} language={language}")
            return candidate

        logger.info(f"topic_planner_duplicate_detected: candidate='{candidate}' similarity={check.get('max_similarity_score', 0)}, retrying...")
        excluded.append(candidate)

    pivot_topic = f"{theme.title()} original variation {uuid4().hex[:8]}"
    logger.info(f"topic_planner_pivoted_topic: topic='{pivot_topic}'")
    return pivot_topic


__all__ = ["build_variation_prompt", "get_fresh_original_topic"]
