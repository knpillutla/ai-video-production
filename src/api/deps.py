"""FastAPI dependency injection for multi-tenant user authentication."""

from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security import decode_access_token
from src.domain.repo import repo
from src.domain.user import User

bearer_scheme = HTTPBearer(auto_error=False)


DEFAULT_USER_EMAIL = "knpillutla@gmail.com"
DEFAULT_USER_ID = UUID("00000000-0000-0000-0000-000000000001")


def get_or_create_default_user() -> User:
    """Ensure default workspace user knpillutla@gmail.com exists in repo."""
    user = repo.get_user(DEFAULT_USER_ID) or repo.get_user_by_email(DEFAULT_USER_EMAIL)
    if not user:
        user = User(
            id=DEFAULT_USER_ID,
            email=DEFAULT_USER_EMAIL,
            display_name="Krishna Pillutla",
            google_sub="google_sub_knpillutla",
            storage_container_name="user-knpillutla-gmail-com",
            api_credit_balance_usd=100.0,
        )
        repo.save_user(user)
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> User:
    """Validate JWT token or inject default user knpillutla@gmail.com for local studio."""
    if not credentials or not credentials.credentials:
        return get_or_create_default_user()

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload.get("sub"))
        user = repo.users.get(user_id)
        if user:
            return user
    except Exception:
        pass
    return get_or_create_default_user()


__all__ = ["get_current_user", "bearer_scheme", "get_or_create_default_user"]
