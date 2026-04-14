from __future__ import annotations


def completion_percent(total: int, complete: int) -> float:
    return 0.0 if total == 0 else round((complete / total) * 100.0, 2)
