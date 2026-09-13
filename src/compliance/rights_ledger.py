"""Asset Rights Ledger for Commercial Clearance Verification."""

from uuid import UUID
from src.core.telemetry import logger
from src.domain.rights import (
    AssetRightsRecord,
    AssetType,
    CommercialLicenseType,
)


class RightsLedger:
    """Manages immutable commercial rights and licensing records for all generated assets."""

    def __init__(self):
        # In-memory ledger partitioned by episode_id
        self._ledger: dict[str, list[AssetRightsRecord]] = {}

    def record_asset(
        self,
        episode_id: UUID | str,
        asset_type: AssetType,
        file_path: str,
        provider: str,
        model_name: str,
        license_type: CommercialLicenseType = CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
        license_id: str = "COMM-STD-2026",
        cleared: bool = True,
        attribution_required: bool = False,
        attribution_text: str | None = None,
        prompt_hash: str | None = None,
    ) -> AssetRightsRecord:
        """Register a generated asset in the rights ledger with license verification."""
        ep_key = str(episode_id)
        if ep_key not in self._ledger:
            self._ledger[ep_key] = []

        record = AssetRightsRecord(
            asset_type=asset_type,
            file_path=file_path,
            provider=provider,
            model_name=model_name,
            license_type=license_type,
            license_id=license_id,
            cleared_for_commercial_monetization=cleared and (license_type != CommercialLicenseType.UNVERIFIED),
            attribution_required=attribution_required,
            attribution_text=attribution_text,
            prompt_hash=prompt_hash,
        )

        self._ledger[ep_key].append(record)
        logger.info(
            f"asset_rights_recorded: ep={ep_key}, type={asset_type}, "
            f"provider={provider}, cleared={record.cleared_for_commercial_monetization}"
        )
        return record

    def get_records_for_episode(self, episode_id: UUID | str) -> list[AssetRightsRecord]:
        """Retrieve all recorded asset licenses for a specific episode."""
        return list(self._ledger.get(str(episode_id), []))

    def verify_episode_rights(self, episode_id: UUID | str) -> tuple[bool, list[str]]:
        """Verify that 100% of episode assets have cleared commercial licenses.

        Returns:
            tuple[bool, list[str]]: (all_cleared, list_of_violations)
        """
        records = self.get_records_for_episode(episode_id)
        if not records:
            return False, ["No asset rights recorded for episode"]

        violations: list[str] = []
        for rec in records:
            if not rec.cleared_for_commercial_monetization:
                violations.append(
                    f"Asset {rec.file_path} ({rec.provider}/{rec.model_name}) is NOT cleared for commercial use."
                )
            if rec.license_type == CommercialLicenseType.UNVERIFIED:
                violations.append(f"Asset {rec.file_path} has UNVERIFIED license status.")

        is_cleared = len(violations) == 0
        if not is_cleared:
            logger.warning(f"rights_verification_failed: ep={episode_id}, violations={len(violations)}")
        else:
            logger.info(f"rights_verification_passed: ep={episode_id}, assets_cleared={len(records)}")

        return is_cleared, violations

    def clear_ledger(self, episode_id: UUID | str | None = None) -> None:
        """Clear ledger records (useful for test resets)."""
        if episode_id:
            self._ledger.pop(str(episode_id), None)
        else:
            self._ledger.clear()


rights_ledger = RightsLedger()

__all__ = ["RightsLedger", "rights_ledger"]
