"""YouTube Partner Program (YPP) Monetization Safety and AdSense Screener."""

import re
from typing import Final

ADSENSE_RULES: Final[dict[str, list[str]]] = {
    "hate_speech": [r"\bhate\b", r"\bracist\b", r"\bbigot\b", r"\bsupremacist\b"],
    "violence": [r"\bgore\b", r"\bdecapitat\w*", r"\bmurder\b", r"\bblood bath\b"],
    "dangerous_acts": [r"\bself[\s-]harm\b", r"\bsuicide\b", r"\bpoison\b", r"\blethal\b"],
    "harassment": [r"\bstalk\w*", r"\bdoxx\w*", r"\bblackmail\b"],
    "adult_content": [r"\bnsfw\b", r"\bporn\w*", r"\bexplicit sex\b"],
    "firearms": [r"\bghost gun\b", r"\bunregistered firearm\b", r"\bbomb making\b"],
    "drugs": [r"\bmethamphetamine\b", r"\bheroin\b", r"\bcocaine\b"],
    "tobacco": [r"\bvape promotion\b", r"\bbuy cigarettes\b"],
    "sensitive_events": [r"\bterror attack hoax\b", r"\bmass shooting conspiracy\b"],
    "profanity": [r"\bfuck\b", r"\bshit\b", r"\bbitch\b", r"\basshole\b"],
    "misinformation": [r"\belection fraud hoax\b", r"\bmedical miracle cure\b"],
}

OPENING_SEVEN_SEC_PROFANITY: Final[list[str]] = [
    r"\bfuck\b", r"\bshit\b", r"\bbitch\b", r"\bdamn\b", r"\bass\b"
]


def screen_script_for_adsense(script_text: str) -> dict[str, list[str]]:
    """Screen complete narrative script against all 11 AdSense demonetization categories."""
    findings: dict[str, list[str]] = {}
    lower_text = script_text.lower()

    for category, patterns in ADSENSE_RULES.items():
        matches = []
        for pat in patterns:
            if re.search(pat, lower_text):
                matches.append(pat)
        if matches:
            findings[category] = matches

    return findings


def screen_opening_profanity(opening_script_text: str) -> list[str]:
    """Screen opening 7 seconds against YouTube's strict zero-profanity rule."""
    violations = []
    lower = opening_script_text.lower()
    for pat in OPENING_SEVEN_SEC_PROFANITY:
        if re.search(pat, lower):
            violations.append(pat)
    return violations


def evaluate_ypp_safety(
    script_text: str,
    opening_text: str = "",
    originality_score: float = 0.95,
) -> dict:
    """Evaluate end-to-end monetization safety for YouTube Partner Program."""
    adsense_violations = screen_script_for_adsense(script_text)
    opening_violations = screen_opening_profanity(opening_text or script_text[:120])

    is_safe = len(adsense_violations) == 0 and len(opening_violations) == 0 and (originality_score >= 0.80)
    risk_level = "LOW" if is_safe else ("MEDIUM" if len(adsense_violations) <= 1 else "HIGH")

    return {
        "is_monetization_safe": is_safe,
        "risk_level": risk_level,
        "adsense_violations": adsense_violations,
        "opening_profanity_violations": opening_violations,
        "originality_score": originality_score,
        "requires_human_arbitration": not is_safe,
    }


def get_synthetic_media_disclosure() -> dict:
    """Build YouTube Data API synthetic media disclosure payload."""
    return {
        "status": {
            "containsSyntheticMedia": True,
            "selfDeclaredMadeForKids": False,
        },
        "c2pa": {
            "claim_generator": "CineAIStudio/2.0 (Phase 3)",
            "assertions": ["c2pa.actions.created", "c2pa.actions.synthesized"],
        },
    }


__all__ = [
    "screen_script_for_adsense",
    "screen_opening_profanity",
    "evaluate_ypp_safety",
    "get_synthetic_media_disclosure",
]
