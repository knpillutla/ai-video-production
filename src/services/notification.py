"""Transactional Notification Service for Human-in-the-Loop Review.

Supports SMTP email dispatching, tokenized 1-click approvals, and channel master review gates.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Optional
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
    episode_id: str
    episode_title: str
    preview_video_path: str
    magic_approval_token: str
    compliance_score: float = 0.98
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

    def _send_smtp_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP if credentials are configured in environment."""
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        from_email = os.getenv("SMTP_FROM", smtp_user or "no-reply@cineai.studio")

        if not (smtp_host and smtp_user and smtp_pass):
            logger.info("smtp_not_configured: Email logged to console and memory.")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, [to_email], msg.as_string())
            logger.info(f"smtp_email_sent_successfully: to='{to_email}' subject='{subject}'")
            return True
        except Exception as err:
            logger.error(f"smtp_send_failed: {err}")
            return False

    async def notify_channel_master_ready(
        self,
        channel_name: str,
        episode_id: str,
        title: str,
        master_video_path: str,
        short_video_path: Optional[str] = None,
        long_play_hours: float = 3.0,
        stretch_script: str = "stretch_earth_serenade.py",
        recipient_email: Optional[str] = None,
    ) -> EmailNotification:
        """Send notification when a 60s/120s 4K master video is ready for creator approval."""
        to_email = recipient_email or os.getenv("CREATOR_EMAIL", "creator@youtube.studio")
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        token = f"master_rev_{uuid4().hex[:16]}"
        subject = f"Master Ready for Review: '{title}' [{channel_name}]"
        direct_confirm_url = f"{base_url}/api/approvals/quick-confirm?token={token}"
        cli_command = f"python scripts/channels/{stretch_script} --id {episode_id}"

        html_body = f"""
        <div style='font-family: sans-serif; background: #080c15; color: #fff; padding: 28px; border-radius: 12px; max-width: 600px;'>
          <h2 style='color: #10b981; margin-top: 0;'>4K Master Video Ready for Review</h2>
          <p>Channel: <strong>{channel_name}</strong></p>
          <p>Episode: <strong>{title}</strong> (ID: <code>{episode_id}</code>)</p>
          <div style='background: #0f1626; border: 1px solid #1e293b; padding: 16px; border-radius: 8px; margin: 16px 0;'>
            <p style='margin: 4px 0;'><strong>4K Master Path:</strong> <code>{master_video_path}</code></p>
            {f"<p style='margin: 4px 0;'><strong>9:16 Short Path:</strong> <code>{short_video_path}</code></p>" if short_video_path else ""}
            <p style='margin: 4px 0;'><strong>Target Long-Play Duration:</strong> {long_play_hours} Hours</p>
          </div>
          <div style='margin: 24px 0;'>
            <a href='{direct_confirm_url}' style='background: #10b981; color: #fff; padding: 14px 28px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block;'>
              ⚡ Approve & Stretch to {long_play_hours} Hours Long-Play
            </a>
          </div>
          <p style='color: #94a3b8; font-size: 13px;'>Or approve via CLI terminal:</p>
          <pre style='background: #020617; padding: 12px; border-radius: 6px; color: #38bdf8; font-size: 12px;'>{cli_command}</pre>
        </div>
        """

        notification = EmailNotification(
            recipient_email=to_email,
            subject=subject,
            episode_id=episode_id,
            episode_title=title,
            preview_video_path=master_video_path,
            magic_approval_token=token,
            compliance_score=0.98,
            direct_confirm_url=direct_confirm_url,
            html_body=html_body,
        )

        self._token_store[token] = {
            "token": token,
            "episode_id": episode_id,
            "channel_name": channel_name,
            "recipient_email": to_email,
            "created_at": datetime.now(timezone.utc),
            "used": False,
        }

        self.sent_emails.append(notification)
        self._send_smtp_email(to_email, subject, html_body)

        print("\n" + "=" * 70)
        print(f"[NOTIFICATION] HUMAN-IN-THE-LOOP REVIEW NOTIFICATION DISPATCHED")
        print(f"To:          {to_email}")
        print(f"Subject:     {subject}")
        print(f"1-Click URL: {direct_confirm_url}")
        print(f"CLI Approve: {cli_command}")
        print("=" * 70 + "\n")
        return notification

    async def notify_keyframes_ready(
        self,
        channel_name: str,
        episode_id: str,
        title: str,
        keyframe_paths: list[str],
        recipient_email: Optional[str] = None,
        pipeline_script: str = "nature_sanctuary_pipeline.py",
    ) -> EmailNotification:
        """Send notification when 4K keyframe photos are synthesized and ready for creator approval."""
        to_email = recipient_email or os.getenv("CREATOR_EMAIL", "creator@youtube.studio")
        base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        token = f"photo_rev_{uuid4().hex[:16]}"
        subject = f"Photos Ready for Review: '{title}' [{channel_name}]"
        direct_confirm_url = f"{base_url}/api/approvals/quick-confirm?token={token}"
        cli_command = f"python scripts/channels/{pipeline_script} --id {episode_id}"

        kf_list_html = "".join(f"<li style='margin: 4px 0;'><code>{p}</code></li>" for p in keyframe_paths)
        html_body = f"""
        <div style='font-family: sans-serif; background: #080c15; color: #fff; padding: 28px; border-radius: 12px; max-width: 600px;'>
          <h2 style='color: #38bdf8; margin-top: 0;'>4K Keyframe Photos Ready for Review</h2>
          <p>Channel: <strong>{channel_name}</strong></p>
          <p>Episode: <strong>{title}</strong> (ID: <code>{episode_id}</code>)</p>
          <div style='background: #0f1626; border: 1px solid #1e293b; padding: 16px; border-radius: 8px; margin: 16px 0;'>
            <p style='margin: 4px 0; font-weight: bold;'>Synthesized 4K Photos ({len(keyframe_paths)} Images):</p>
            <ul style='padding-left: 20px; color: #cbd5e1;'>{kf_list_html}</ul>
          </div>
          <p style='color: #94a3b8;'>To approve photos and synthesize video motion from CLI, run:</p>
          <div style='background: #020617; padding: 10px 14px; border-radius: 6px; font-family: monospace; font-size: 13px; color: #a5f3fc; margin-bottom: 20px;'>
            {cli_command}
          </div>
          <div style='margin: 24px 0;'>
            <a href='{direct_confirm_url}' style='background: #38bdf8; color: #080c15; padding: 14px 28px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block;'>
              Approve Photos & Synthesize Video Motion
            </a>
          </div>
        </div>
        """

        notification = EmailNotification(
            recipient_email=to_email,
            subject=subject,
            episode_id=episode_id,
            episode_title=title,
            preview_video_path=keyframe_paths[0] if keyframe_paths else "",
            magic_approval_token=token,
            compliance_score=0.98,
            direct_confirm_url=direct_confirm_url,
            html_body=html_body,
        )

        self._token_store[token] = {
            "token": token,
            "episode_id": episode_id,
            "channel_name": channel_name,
            "action": "photos_approved",
            "recipient_email": to_email,
            "created_at": datetime.now(timezone.utc),
            "used": False,
        }

        self.sent_emails.append(notification)
        self._send_smtp_email(to_email, subject, html_body)

        print("\n" + "=" * 70)
        print(f"[NOTIFICATION] KEYFRAME PHOTOS READY FOR HUMAN REVIEW ({len(keyframe_paths)} Images)")
        print(f"To:          {to_email}")
        print(f"Subject:     {subject}")
        for idx, kf in enumerate(keyframe_paths, 1):
            print(f"Shot {idx}:     {kf}")
        print(f"1-Click URL: {direct_confirm_url}")
        print(f"CLI Resume:  {cli_command}")
        print("=" * 70 + "\n")
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
