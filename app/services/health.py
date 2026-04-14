from __future__ import annotations


def freshness_label(minutes_since_sync: int) -> str:
    if minutes_since_sync < 30:
        return "fresh"
    if minutes_since_sync < 240:
        return "warning"
    if minutes_since_sync < 1440:
        return "stale"
    return "critical stale"


def delivery_health(overdue: int, critical_overdue: int) -> str:
    if critical_overdue > 0 or overdue > 10:
        return "Red"
    if overdue > 3:
        return "Yellow"
    return "Green"
