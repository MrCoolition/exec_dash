from __future__ import annotations


def feature_flags_for_tenant(_tenant_slug: str) -> dict[str, bool]:
    return {"releases_enabled": False, "ado_analytics": False}
