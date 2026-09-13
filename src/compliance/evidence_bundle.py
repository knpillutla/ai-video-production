"""Originality and Provenance Evidence Bundle Packager."""

import json
from pathlib import Path
from uuid import UUID
from src.compliance.rights_ledger import rights_ledger
from src.core.telemetry import logger
from src.domain.rights import OriginalityEvidenceBundle


def build_evidence_bundle(
    project_id: UUID,
    episode_id: UUID,
    title: str,
    script_thesis: str,
    research_sources: list[dict] | None = None,
    originality_score: float = 0.95,
) -> OriginalityEvidenceBundle:
    """Compile an auditable provenance bundle verifying originality and commercial rights."""
    records = rights_ledger.get_records_for_episode(episode_id)
    all_cleared, _ = rights_ledger.verify_episode_rights(episode_id)

    bundle = OriginalityEvidenceBundle(
        project_id=project_id,
        episode_id=episode_id,
        title=title,
        script_thesis=script_thesis,
        research_sources=research_sources or [],
        originality_score=originality_score,
        rights_records=records,
        total_assets_cleared=len([r for r in records if r.cleared_for_commercial_monetization]),
        monetization_approved=all_cleared and (originality_score >= 0.80),
    )
    return bundle


def save_evidence_bundle(
    bundle: OriginalityEvidenceBundle,
    output_dir: Path | str,
) -> Path:
    """Serialize and write the evidence bundle to the episode's storage vault."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / "evidence_bundle.json"

    # Serialize with ISO datetime formatting
    data = json.loads(bundle.model_dump_json())
    bundle_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info(f"evidence_bundle_archived: path={bundle_path}, approved={bundle.monetization_approved}")
    return bundle_path


__all__ = ["build_evidence_bundle", "save_evidence_bundle"]
