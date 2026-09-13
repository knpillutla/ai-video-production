"""User-scoped Show and Character management API routes."""

import re
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_current_user
from src.core.storage import storage_service
from src.domain.creative import Character, CharacterCreate, Show, ShowCreate
from src.domain.repo import repo
from src.domain.user import User

router = APIRouter(prefix="/api/shows", tags=["Shows & Characters"])


def slugify(title: str) -> str:
    """Generate clean filesystem slug from title."""
    clean = re.sub(r"[^\w\s-]", "", title).strip().lower()
    return re.sub(r"[-\s]+", "_", clean)


@router.post("", response_model=Show, status_code=status.HTTP_201_CREATED)
async def create_show(req: ShowCreate, current_user: User = Depends(get_current_user)):
    """Create a new show universe under the authenticated user's creative vault."""
    slug = slugify(req.title)
    show = Show(
        user_id=current_user.id,
        title=req.title,
        slug=slug,
        genre=req.genre,
        synopsis=req.synopsis,
    )
    saved_show = repo.save_show(show)
    # Ensure physical folder structure in user's container
    vault_path = storage_service.get_creative_vault_path(str(current_user.id), slug)
    await storage_service.save_json(vault_path / "series_metadata.json", saved_show.model_dump(mode="json"))
    return saved_show


@router.get("", response_model=list[Show])
async def list_shows(current_user: User = Depends(get_current_user)):
    """List only shows owned by the current authenticated user."""
    return repo.list_shows(current_user.id)


@router.get("/{show_id}", response_model=Show)
async def get_show(show_id: UUID, current_user: User = Depends(get_current_user)):
    """Get details of a specific show owned by the user."""
    show = repo.get_show(current_user.id, show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return show


@router.post("/{show_id}/characters", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(show_id: UUID, req: CharacterCreate, current_user: User = Depends(get_current_user)):
    """Add a persistent character to a show universe."""
    show = repo.get_show(current_user.id, show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")

    character = Character(
        user_id=current_user.id,
        show_id=show_id,
        name=req.name,
        age_bracket=req.age_bracket,
        gender=req.gender,
        backstory=req.backstory,
        voice_profile_id=req.voice_profile_id,
    )
    saved_char = repo.save_character(character)
    # Ensure character folder in user's creative vault
    char_slug = slugify(req.name)
    char_path = storage_service.get_character_path(str(current_user.id), show.slug, char_slug)
    await storage_service.save_json(char_path / "character_profile.json", saved_char.model_dump(mode="json"))
    return saved_char


@router.get("/{show_id}/characters", response_model=list[Character])
async def list_characters(show_id: UUID, current_user: User = Depends(get_current_user)):
    """List characters for a show owned by the user."""
    show = repo.get_show(current_user.id, show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Show not found")
    return repo.list_characters(current_user.id, show_id)
