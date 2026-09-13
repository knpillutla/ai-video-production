"""Google OAuth 2.0 and session management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.core.security import create_access_token, verify_google_id_token
from src.core.storage import sanitize_container_name, storage_service
from src.domain.repo import repo
from src.domain.user import SubscriptionTier, User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class GoogleLoginRequest(BaseModel):
    id_token: str


class TestTokenRequest(BaseModel):
    email: str
    display_name: str
    subscription_tier: SubscriptionTier = SubscriptionTier.CREATOR


class AuthResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    user: User


@router.post("/google", response_model=AuthResponse)
async def login_google(req: GoogleLoginRequest):
    """Authenticate with Google ID token, register user, and ensure private storage container."""
    try:
        user_info = await verify_google_id_token(req.id_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    email = user_info["email"]
    user = repo.get_user_by_email(email)

    if not user:
        # Register new user and auto-provision private container
        temp_user = User(
            email=email,
            display_name=user_info.get("name", email.split("@")[0]),
            avatar_url=user_info.get("picture"),
            google_sub=user_info.get("sub", ""),
            storage_container_name="pending",
        )
        temp_user.storage_container_name = sanitize_container_name(str(temp_user.id))
        user = repo.save_user(temp_user)
        # Ensure container exists on disk / cloud
        storage_service.get_user_container_path(str(user.id))

    token = create_access_token(str(user.id), user.email, user.display_name)
    return AuthResponse(token=token, user=user)


@router.post("/test-token", response_model=AuthResponse)
async def create_test_token(req: TestTokenRequest):
    """Local development endpoint to issue tokens without external Google sign-in."""
    user = repo.get_user_by_email(req.email)
    if not user:
        temp_user = User(
            email=req.email,
            display_name=req.display_name,
            google_sub=f"dev_{abs(hash(req.email))}",
            subscription_tier=req.subscription_tier,
            storage_container_name="pending",
        )
        temp_user.storage_container_name = sanitize_container_name(str(temp_user.id))
        user = repo.save_user(temp_user)
        storage_service.get_user_container_path(str(user.id))

    token = create_access_token(str(user.id), user.email, user.display_name)
    return AuthResponse(token=token, user=user)


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return currently authenticated user profile."""
    return current_user
