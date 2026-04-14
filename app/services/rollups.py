from __future__ import annotations

from app.services.metrics import completion_percent


def overview_rollup(items: list[dict]) -> dict[str, int | float]:
    total = len(items)
    complete = sum(1 for i in items if i.get("state") == "Done")
    overdue = sum(1 for i in items if i.get("is_overdue"))
    return {
        "total": total,
        "complete": complete,
        "overdue": overdue,
        "completion_percent": completion_percent(total, complete),
    }
