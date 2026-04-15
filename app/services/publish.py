from __future__ import annotations

from sqlalchemy import text

from app.db import connection


def publish_weekly_update(weekly_update_id: str, submitted_by_user_id: str | None) -> None:
    with connection() as conn:
        conn.execute(
            text("SELECT publish_weekly_update(:weekly_update_id, :submitted_by_user_id)"),
            {
                "weekly_update_id": weekly_update_id,
                "submitted_by_user_id": submitted_by_user_id,
            },
        )
