"""Publisher MCP Server for YouTube Data API v3 payload construction and monetization gate."""

from typing import Any
from src.mcp.base import MCPServerBase

server = MCPServerBase(server_name="mcp-publisher", version="1.0.0")


async def prepare_youtube_payload(
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy_status: str = "private",
    category_id: str = "23",
    contains_synthetic_media: bool = True,
    subtitle_tracks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Assemble YouTube Data API v3 upload payload with synthetic media disclosure."""
    clean_tags = tags or ["TeluguComedy", "WFH", "AIStudio", "Shorts"]
    clean_subs = subtitle_tracks or [
        {"language": "en", "name": "English (Default)", "is_default": True},
        {"language": "te", "name": "Telugu (తెలుగు)", "is_default": False},
        {"language": "hi", "name": "Hindi (हिन्दी)", "is_default": False},
    ]

    payload = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": clean_tags[:30],
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
        },
        "contentDetails": {
            "containsSyntheticMedia": contains_synthetic_media,
            "syntheticMediaDetails": {
                "alteredVisuals": True,
                "synthesizedAudio": True,
            },
        },
        "captions": clean_subs,
    }
    return {
        "payload": payload,
        "is_ready_for_upload": True,
        "contains_synthetic_disclosure": contains_synthetic_media,
        "total_caption_tracks": len(clean_subs),
    }


async def validate_monetization_readiness(
    episode_id: str,
    rights_cleared: bool = True,
    qa_passed: bool = True,
    has_evidence_bundle: bool = True,
) -> dict[str, Any]:
    """Validate that episode is 100% monetizable prior to initiating channel publication."""
    blocks: list[str] = []
    if not rights_cleared:
        blocks.append("Uncleared commercial assets detected in rights ledger")
    if not qa_passed:
        blocks.append("Technical video QA failed (-14 LUFS or frame defects)")
    if not has_evidence_bundle:
        blocks.append("Missing provenance evidence bundle")

    can_publish = len(blocks) == 0
    return {
        "episode_id": episode_id,
        "ready_to_publish": can_publish,
        "blocking_reasons": blocks,
        "monetization_status": "Eligible for Full Monetization" if can_publish else "Blocked",
    }


server.register_tool(
    name="mcp_prepare_youtube_payload",
    description="Assemble YouTube Data API v3 upload payload with tags and synthetic disclosure",
    input_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "privacy_status": {"type": "string", "default": "private"},
            "contains_synthetic_media": {"type": "boolean", "default": True},
        },
        "required": ["title", "description"],
    },
    handler=prepare_youtube_payload,
)

server.register_tool(
    name="mcp_validate_monetization_readiness",
    description="Validate commercial clearance and QA score before YouTube upload",
    input_schema={
        "type": "object",
        "properties": {
            "episode_id": {"type": "string"},
            "rights_cleared": {"type": "boolean", "default": True},
            "qa_passed": {"type": "boolean", "default": True},
            "has_evidence_bundle": {"type": "boolean", "default": True},
        },
        "required": ["episode_id"],
    },
    handler=validate_monetization_readiness,
)

if __name__ == "__main__":
    server.run_cli()
