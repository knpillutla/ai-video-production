"""Post-Render Quality Assurance & Monetization Gate Agent."""

from pathlib import Path
from uuid import UUID
from src.compliance.rights_ledger import rights_ledger
from src.compliance.ypp_safety import evaluate_ypp_safety
from src.core.telemetry import logger
from src.domain.qa import VideoQAReport
from src.scripts.local_video_qa import run_video_qa_audit


class QAGateAgent:
    """Arbitrates publish eligibility across Video QA, Rights Ledger, and AdSense Safety."""

    def audit_rendered_episode(
        self,
        episode_id: UUID | str,
        video_path: Path | str,
        script_text: str = "",
        duration_seconds: float = 12.0,
    ) -> tuple[bool, VideoQAReport, list[str]]:
        """Audit master video and determine whether publish gate is granted.

        Returns:
            tuple[bool, VideoQAReport, list[str]]: (publish_eligible, qa_report, blocking_reasons)
        """
        blocking_reasons: list[str] = []

        # 1. Commercial Rights Check
        rights_cleared, rights_violations = rights_ledger.verify_episode_rights(episode_id)
        if not rights_cleared:
            blocking_reasons.extend(rights_violations)

        # 2. AdSense & YPP Monetization Check
        if script_text:
            safety = evaluate_ypp_safety(script_text)
            if not safety["is_monetization_safe"]:
                for cat, pats in safety["adsense_violations"].items():
                    blocking_reasons.append(f"AdSense Safety Violation in category '{cat}': {pats}")
                if safety["opening_profanity_violations"]:
                    blocking_reasons.append(f"Profanity in opening 7s: {safety['opening_profanity_violations']}")

        # 3. Post-Render Technical Video QA Check
        qa_report = run_video_qa_audit(video_path, duration_seconds=duration_seconds)
        if not qa_report.passed:
            if not qa_report.loudness.lufs_passed:
                blocking_reasons.append(
                    f"Loudness out of spec: {qa_report.loudness.integrated_lufs:.1f} LUFS (Target: -14.0 LUFS)"
                )
            if not qa_report.defects.defects_passed:
                blocking_reasons.append(
                    f"Frame defects detected: black frames={qa_report.defects.black_duration_seconds}s, "
                    f"frozen={qa_report.defects.frozen_duration_seconds}s"
                )

        publish_eligible = len(blocking_reasons) == 0
        if publish_eligible:
            logger.info(f"qa_gate_approved: ep={episode_id}, score={qa_report.scores.composite_score}")
        else:
            logger.warning(f"qa_gate_blocked: ep={episode_id}, reasons={blocking_reasons}")

        return publish_eligible, qa_report, blocking_reasons


qa_gate_agent = QAGateAgent()

__all__ = ["QAGateAgent", "qa_gate_agent"]
