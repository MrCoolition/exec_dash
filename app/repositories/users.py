from __future__ import annotations

from app.db import fetch_one


def upsert_user(provider: str, provider_sub: str, email: str | None, display_name: str | None) -> dict:
    return fetch_one(
        """
        INSERT INTO users (provider, provider_sub, email, display_name)
        VALUES (:provider, :provider_sub, :email, :display_name)
        ON CONFLICT (provider_sub) DO UPDATE SET
            email = EXCLUDED.email,
            display_name = EXCLUDED.display_name
        RETURNING id::text AS id, provider, provider_sub, email, display_name
        """,
        {
            "provider": provider,
            "provider_sub": provider_sub,
            "email": email,
            "display_name": display_name,
        },
    ) or {}
