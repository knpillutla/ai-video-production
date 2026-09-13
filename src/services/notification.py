"""Transactional Notification Service for Human-in-the-Loop Review."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.domain.creative import Episode
from src.domain.user import User


class EmailNotification(BaseModel):
    """Immutable record of an approval notification email sent to creator."""

    id: UUID = Field(default_factory=uuid4)
    recipient_email: str
    subject: str
    episode_id: UUID
    episode_title: str
    preview_video_path: str
    magic_approval_token: str
    compliance_score: float
    direct_confirm_url: str = ""
    studio_review_url: str = ""
    html_body: str = ""
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "delivered"


class NotificationService:
    """Dispatches email notifications for human-in-the-loop review and monetization gates."""

    def __init__(self):
        self.sent_emails: list[EmailNotification] = []
        self._token_store: dict[str, dict[str, Any]] = {}

    async def send_approval_request_email(
        self,
        user: User,
        episode: Episode,
        video_path: str | None = None,
        compliance_score: float = 0.96,
        base_url: str = "http://localhost:8000",
    ) -> EmailNotification:
        """Send an interactive email notifying the user that a scheduled video needs review."""
        token = f"magic_review_{uuid4().hex[:16]}"
        subject = f"🎬 Action Required: Review & Approve '{episode.title}' for YouTube Broadcast"
        direct_confirm_url = f"{base_url}/api/approvals/quick-confirm?token={token}"
        studio_review_url = f"{base_url}/ui?approval_id={episode.id}&token={token}"

        html_body = (
            f"<div style='font-family: sans-serif; background: #080c15; color: #fff; padding: 24px; border-radius: 12px;'>"
            f"  <h2 style='color: #818cf8;'>🎬 Episode Ready for Broadcast Approval</h2>"
            f"  <p>Your scheduled video <strong>{episode.title}</strong> has finished rendering.</p>"
            f"  <p><strong>AdSense Monetization Score:</strong> {int(compliance_score * 100)}% Passed (C2PA Synthesized)</p>"
            f"  <div style='margin: 20px 0;'>"
            f"    <a href='{direct_confirm_url}' style='background: #10b981; color: #fff; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block; margin-right: 12px;'>"
            f"      ⚡ 1-Click Approve & Publish (No Login Required)"
            f"    </a>"
            f"    <a href='{studio_review_url}' style='background: #4f46e5; color: #fff; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block;'>"
            f"      🖥️ Review in CineAI Studio"
            f"    </a>"
            f"  </div>"
            f"  <p style='color: #94a3b8; font-size: 12px;'>Direct confirm broadcasts immediately without logging in. Review in Studio will prompt for login if you do not have an active session.</p>"
            f"</div>"
        )

        notification = EmailNotification(
            recipient_email=user.email,
            subject=subject,
            episode_id=episode.id,
            episode_title=episode.title,
            preview_video_path=video_path or episode.master_video_path or "/preview/default.mp4",
            magic_approval_token=token,
            compliance_score=compliance_score,
            direct_confirm_url=direct_confirm_url,
            studio_review_url=studio_review_url,
            html_body=html_body,
        )

        self._token_store[token] = {
            "token": token,
            "user_id": user.id,
            "episode_id": episode.id,
            "recipient_email": user.email,
            "created_at": datetime.now(timezone.utc),
            "used": False,
        }

        self.sent_emails.append(notification)
        logger.info(
            f"approval_email_dispatched: to='{user.email}' ep_id={episode.id} "
            f"token={token} score={compliance_score}"
        )
        return notification

    def get_token_data(self, token: str) -> dict[str, Any] | None:
        """Fetch token metadata if valid and unused."""
        data = self._token_store.get(token)
        if data and not data.get("used", False):
            return data
        return None

    def consume_token(self, token: str) -> dict[str, Any] | None:
        """Mark token as used and return payload."""
        data = self._token_store.get(token)
        if data and not data.get("used", False):
            data["used"] = True
            data["consumed_at"] = datetime.now(timezone.utc)
            return data
        return None

    def list_notifications(self, user_email: str | None = None) -> list[EmailNotification]:
        """Retrieve historical sent email notifications."""
        if user_email:
            return [e for e in self.sent_emails if e.recipient_email.lower() == user_email.lower()]
        return list(self.sent_emails)

    def clear(self) -> None:
        """Clear notification and token history (for test isolation)."""
        self.sent_emails.clear()
        self._token_store.clear()


notification_service = NotificationService()
__all__ = ["NotificationService", "notification_service", "EmailNotification"]
