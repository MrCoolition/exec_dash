from __future__ import annotations

from app.db import fetch_all


def list_active_tenants() -> list[dict]:
    return fetch_all(
        """
        SELECT id::text AS id,
               slug,
               name,
               tenant_type,
               is_active,
               created_at,
               updated_at
        FROM tenants
        WHERE is_active IS TRUE
        """
    )
