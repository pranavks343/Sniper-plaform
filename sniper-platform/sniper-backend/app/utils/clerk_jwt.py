"""Verify Clerk-issued JWTs using Clerk's JWKS URL."""
from __future__ import annotations

import logging
from typing import Any

import jwt
from jwt import PyJWKClient

logger = logging.getLogger(__name__)

# Clerk uses RS256
ALLOWED_ALGORITHMS = ["RS256"]


def verify_clerk_token(token: str, jwks_url: str) -> dict[str, Any] | None:
    """
    Verify a JWT issued by Clerk and return the payload, or None if invalid.
    Expects payload to contain sub (Clerk user id) and optionally email.
    """
    if not token or not jwks_url:
        return None
    try:
        client = PyJWKClient(jwks_url, cache_jwk_set=True)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            return None
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=ALLOWED_ALGORITHMS,
            options={"verify_aud": False, "verify_iss": False},
        )
        return payload
    except Exception as exc:  # noqa: BLE001
        logger.debug("Clerk JWT verification failed: %s", exc)
        return None


def clerk_payload_to_user(payload: dict[str, Any]) -> dict[str, str]:
    """Map Clerk JWT payload to our get_current_user shape: user_id, email."""
    sub = payload.get("sub") or ""
    email = payload.get("email") or payload.get("primary_email") or ""
    if not email and isinstance(payload.get("email_addresses"), list):
        first = payload["email_addresses"][0]
        if isinstance(first, dict):
            email = first.get("email") or ""
    if not isinstance(email, str):
        email = ""
    return {"user_id": sub, "email": email or f"{sub}@clerk"}
