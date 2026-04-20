from __future__ import annotations

from app.db import _to_psycopg2_query, connection


def publish_weekly_update(weekly_update_id: str, submitted_by_user_id: str | None) -> None:
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            _to_psycopg2_query("SELECT publish_weekly_update(:weekly_update_id, :submitted_by_user_id)"),
            {
                "weekly_update_id": weekly_update_id,
                "submitted_by_user_id": submitted_by_user_id,
            },
        )
