from __future__ import annotations

from app.db import fetch_all


def count_by_state() -> list[tuple[str, int]]:
    rows = fetch_all(
        """
        SELECT COALESCE(state, 'Unknown') AS state,
               COUNT(*)::int AS count
        FROM work_item_current
        GROUP BY COALESCE(state, 'Unknown')
        """
    )
    return [(str(row["state"]), int(row["count"])) for row in rows]
