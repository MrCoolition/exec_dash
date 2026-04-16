from __future__ import annotations

from datetime import date, datetime


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def has_text(value: str | None) -> bool:
    return bool(normalize_text(value))


def format_date(value: date | datetime | str | None) -> str:
    if not value:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%b %d, %Y")
    if isinstance(value, date):
        return value.strftime("%b %d, %Y")
    try:
        parsed = date.fromisoformat(str(value))
        return parsed.strftime("%b %d, %Y")
    except ValueError:
        return str(value)


def status_class(status: str | None) -> str:
    mapping = {
        "on track": "status-good",
        "needs attention": "status-warn",
        "at risk": "status-bad",
        "complete": "status-good",
        "done": "status-good",
    }
    return mapping.get((status or "").strip().lower(), "status-neutral")


def status_label(status: str | None) -> str:
    return normalize_text(status) or "Unknown"


def severity_rank(severity: str | None) -> int:
    order = {"high": 0, "medium": 1, "low": 2, "dep": 3}
    return order.get((severity or "").strip().lower(), 4)


def is_real_decision(value: str | None) -> bool:
    return has_text(value)
