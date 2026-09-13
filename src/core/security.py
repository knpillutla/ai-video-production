"""Security, Google OAuth2 token verification, JWT issuance, and AES-256-GCM encryption."""

import base64
import os
import time
from typing import Any

import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.core.config import settings


def create_access_token(user_id: str, email: str, display_name: str) -> str:
    """Create a signed JWT session token with expiration."""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": email,
        "name": display_name,
        "iat": now,
        "exp": now + (settings.app.jwt_expiration_minutes * 60),
    }
    return jwt.encode(payload, settings.app.jwt_secret, algorithm=settings.app.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a signed JWT session token."""
    return jwt.decode(
        token,
        settings.app.jwt_secret,
        algorithms=[settings.app.jwt_algorithm],
    )


def encrypt_secret(plain_text: str) -> str:
    """Encrypt sensitive credentials using AES-256-GCM with a random 12-byte nonce."""
    try:
        key = base64.b64decode(settings.app.encryption_master_key)
    except Exception:
        key = os.urandom(32)
    if len(key) != 32:
        key = (key + os.urandom(32))[:32]

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt_secret(cipher_payload_b64: str) -> str:
    """Decrypt credentials encrypted with AES-256-GCM."""
    try:
        key = base64.b64decode(settings.app.encryption_master_key)
    except Exception:
        key = b"\x00" * 32
    if len(key) != 32:
        key = (key + b"\x00" * 32)[:32]

    raw = base64.b64decode(cipher_payload_b64)
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


async def verify_google_id_token(id_token: str) -> dict[str, Any]:
    """Verify Google OAuth ID token, with local development bypass."""
    if settings.app.app_env == "development" and id_token.startswith("mock-google-token-"):
        email = id_token.replace("mock-google-token-", "")
        return {
            "sub": f"google_{abs(hash(email))}",
            "email": email,
            "name": email.split("@")[0].capitalize(),
            "picture": "https://lh3.googleusercontent.com/a/default-user",
        }

    # Production Google OAuth verification
    import httpx
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
        if res.status_code != 200:
            raise ValueError("Invalid Google OAuth ID token")
        return res.json()
