"""Unit tests for JWT generation, validation, and AES-256-GCM secret encryption."""

import pytest
from src.core.security import (
    create_access_token,
    decode_access_token,
    decrypt_secret,
    encrypt_secret,
    verify_google_id_token,
)


def test_jwt_token_flow():
    """Verify access token creation and decoding."""
    user_id = "c4b8e28f-7f61-4c12-b2df-128a50b89312"
    email = "creator@studio.com"
    name = "Krishna P."

    token = create_access_token(user_id, email, name)
    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert payload["name"] == name
    assert "exp" in payload


def test_aes_256_gcm_encryption_roundtrip():
    """Verify AES-256-GCM symmetric encryption and decryption."""
    secret = "ya29.a0AfH6SMB_secret_youtube_refresh_token_xyz"
    encrypted = encrypt_secret(secret)

    assert encrypted != secret
    assert len(encrypted) > len(secret)

    decrypted = decrypt_secret(encrypted)
    assert decrypted == secret


@pytest.mark.asyncio
async def test_mock_google_id_token_verification():
    """Verify mock token verification in development environment."""
    mock_token = "mock-google-token-developer@studio.com"
    profile = await verify_google_id_token(mock_token)

    assert profile["email"] == "developer@studio.com"
    assert profile["name"] == "Developer"
    assert "sub" in profile
