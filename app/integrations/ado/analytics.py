from __future__ import annotations


def analytics_enabled(feature_flags: dict[str, bool]) -> bool:
    return feature_flags.get("ado_analytics", False)
