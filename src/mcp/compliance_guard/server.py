"""Compliance Guard MCP Server for YPP safety, profanity screening, and rights audit."""

from typing import Any
from uuid import UUID
from src.compliance.rights_ledger import rights_ledger
from src.compliance.ypp_safety import evaluate_ypp_safety
from src.mcp.base import MCPServerBase

server = MCPServerBase(server_name="mcp-compliance-guard", version="1.0.0")


async def validate_compliance(script_text: str) -> dict[str, Any]:
    """Audit script against YouTube 11 advertiser-safety policies and 7-second profanity."""
    safety_res = evaluate_ypp_safety(script_text)
    return {
        "is_monetization_safe": safety_res["is_monetization_safe"],
        "opening_profanity_safe": len(safety_res["opening_profanity_violations"]) == 0,
        "opening_profanity_violations": safety_res["opening_profanity_violations"],
        "adsense_violations": safety_res["adsense_violations"],

        "script_length_chars": len(script_text),
        "synthetic_media_disclosure_required": True,
    }


async def audit_rights_ledger(episode_id: str) -> dict[str, Any]:
    """Verify commercial monetization clearance across 100% of recorded episode assets."""
    try:
        ep_uuid = UUID(episode_id)
    except ValueError:
        return {
            "cleared_for_commercial_monetization": False,
            "violations": [f"Invalid UUID format: '{episode_id}'"],
            "assets_audited_count": 0,
        }

    cleared, violations = rights_ledger.verify_episode_rights(ep_uuid)
    records = rights_ledger.get_records_for_episode(ep_uuid)


    return {
        "episode_id": episode_id,
        "cleared_for_commercial_monetization": cleared,
        "violations": violations,
        "assets_audited_count": len(records),
        "assets": [
            {
                "asset_type": r.asset_type.value,
                "provider": r.provider,
                "model_name": r.model_name,
                "cleared": r.cleared_for_commercial_monetization,
                "license_id": r.license_id,
            }

            for r in records
        ],
    }


server.register_tool(
    name="mcp_validate_compliance",
    description="Validate script against YouTube 11 demonetization categories and opening profanity",
    input_schema={
        "type": "object",
        "properties": {
            "script_text": {"type": "string", "description": "Full script or dialogue text to screen"}
        },
        "required": ["script_text"],
    },
    handler=validate_compliance,
)

server.register_tool(
    name="mcp_audit_rights_ledger",
    description="Audit rights ledger for commercial monetization clearance on all episode assets",
    input_schema={
        "type": "object",
        "properties": {
            "episode_id": {"type": "string", "description": "UUID string of episode project"}
        },
        "required": ["episode_id"],
    },
    handler=audit_rights_ledger,
)

if __name__ == "__main__":
    server.run_cli()
