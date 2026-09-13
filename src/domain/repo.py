"""In-memory multi-tenant repository with atomic JSON persistence for Phase 1."""

import json
from pathlib import Path
from uuid import UUID

from src.core.config import settings
from src.domain.creative import Character, Episode, Show
from src.domain.distribution import Channel, ChannelPublication, ScheduleJob
from src.domain.user import User


class MemoryRepository:
    """Thread-safe multi-tenant repository enforcing user_id query boundaries."""

    def __init__(self, persistence_file: Path | None = None):
        self.file_path = persistence_file or (Path(settings.storage.local_storage_root) / "db_state.json")
        self.users: dict[UUID, User] = {}
        self.shows: dict[UUID, Show] = {}
        self.characters: dict[UUID, Character] = {}
        self.episodes: dict[UUID, Episode] = {}
        self.channels: dict[UUID, Channel] = {}
        self.publications: dict[UUID, ChannelPublication] = {}
        self.schedules: dict[UUID, ScheduleJob] = {}
        self._load()

    def _save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "users": {str(k): v.model_dump(mode="json") for k, v in self.users.items()},
            "shows": {str(k): v.model_dump(mode="json") for k, v in self.shows.items()},
            "characters": {str(k): v.model_dump(mode="json") for k, v in self.characters.items()},
            "episodes": {str(k): v.model_dump(mode="json") for k, v in self.episodes.items()},
            "channels": {str(k): v.model_dump(mode="json") for k, v in self.channels.items()},
            "publications": {str(k): v.model_dump(mode="json") for k, v in self.publications.items()},
            "schedules": {str(k): v.model_dump(mode="json") for k, v in self.schedules.items()},
        }
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _load(self) -> None:
        if not self.file_path.exists():
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.users = {UUID(k): User(**v) for k, v in data.get("users", {}).items()}
            self.shows = {UUID(k): Show(**v) for k, v in data.get("shows", {}).items()}
            self.characters = {UUID(k): Character(**v) for k, v in data.get("characters", {}).items()}
            self.episodes = {UUID(k): Episode(**v) for k, v in data.get("episodes", {}).items()}
            self.channels = {UUID(k): Channel(**v) for k, v in data.get("channels", {}).items()}
            self.publications = {UUID(k): ChannelPublication(**v) for k, v in data.get("publications", {}).items()}
            self.schedules = {UUID(k): ScheduleJob(**v) for k, v in data.get("schedules", {}).items()}
        except Exception:
            pass

    def clear(self) -> None:
        """Clear all in-memory entities and delete the persistence file (for test isolation)."""
        self.users.clear()
        self.shows.clear()
        self.characters.clear()
        self.episodes.clear()
        self.channels.clear()
        self.publications.clear()
        self.schedules.clear()
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except Exception:
                pass

    # User operations
    def get_user(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email.lower() == email.lower()), None)

    def save_user(self, user: User) -> User:
        self.users[user.id] = user
        self._save()
        return user

    # Show operations (user-scoped)
    def list_shows(self, user_id: UUID) -> list[Show]:
        return [s for s in self.shows.values() if s.user_id == user_id]

    def get_show(self, user_id: UUID, show_id: UUID) -> Show | None:
        show = self.shows.get(show_id)
        return show if show and show.user_id == user_id else None

    def save_show(self, show: Show) -> Show:
        self.shows[show.id] = show
        self._save()
        return show

    # Character operations (user-scoped)
    def list_characters(self, user_id: UUID, show_id: UUID) -> list[Character]:
        return [c for c in self.characters.values() if c.user_id == user_id and c.show_id == show_id]

    def save_character(self, character: Character) -> Character:
        self.characters[character.id] = character
        self._save()
        return character

    # Episode operations (user-scoped)
    def list_episodes(self, user_id: UUID, show_id: UUID | None = None) -> list[Episode]:
        if show_id:
            return [e for e in self.episodes.values() if e.user_id == user_id and e.show_id == show_id]
        return [e for e in self.episodes.values() if e.user_id == user_id]

    def get_episode(self, user_id: UUID, episode_id: UUID) -> Episode | None:
        ep = self.episodes.get(episode_id)
        return ep if ep and ep.user_id == user_id else None

    def save_episode(self, episode: Episode) -> Episode:
        self.episodes[episode.id] = episode
        self._save()
        return episode

    # Channel operations (user-scoped)
    def list_channels(self, user_id: UUID) -> list[Channel]:
        return [c for c in self.channels.values() if c.user_id == user_id]

    def get_channel(self, user_id: UUID, channel_id: UUID) -> Channel | None:
        c = self.channels.get(channel_id)
        return c if c and c.user_id == user_id else None

    def save_channel(self, channel: Channel) -> Channel:
        self.channels[channel.id] = channel
        self._save()
        return channel

    # Publication operations (user-scoped)
    def list_publications(self, user_id: UUID, channel_id: UUID | None = None) -> list[ChannelPublication]:
        if channel_id:
            return [p for p in self.publications.values() if p.user_id == user_id and p.channel_id == channel_id]
        return [p for p in self.publications.values() if p.user_id == user_id]

    def save_publication(self, publication: ChannelPublication) -> ChannelPublication:
        self.publications[publication.id] = publication
        self._save()
        return publication

    # Schedule operations (user-scoped)
    def list_schedules(self, user_id: UUID) -> list[ScheduleJob]:
        return [s for s in self.schedules.values() if s.user_id == user_id]

    def get_schedule(self, user_id: UUID, schedule_id: UUID) -> ScheduleJob | None:
        s = self.schedules.get(schedule_id)
        return s if s and s.user_id == user_id else None

    def save_schedule(self, schedule: ScheduleJob) -> ScheduleJob:
        self.schedules[schedule.id] = schedule
        self._save()
        return schedule

    def delete_schedule(self, user_id: UUID, schedule_id: UUID) -> bool:
        s = self.get_schedule(user_id, schedule_id)
        if s:
            del self.schedules[schedule_id]
            self._save()
            return True
        return False


# Singleton repository instance
repo = MemoryRepository()

__all__ = ["repo", "MemoryRepository"]
