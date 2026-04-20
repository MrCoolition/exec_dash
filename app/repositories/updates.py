from __future__ import annotations

from datetime import date

from app.db import fetch_one


def get_weekly_update(tenant_id: str, week_ending: date) -> dict | None:
    return fetch_one(
        """
        SELECT id::text AS id,
               tenant_id::text AS tenant_id,
               ado_project_id::text AS ado_project_id,
               week_ending,
               executive_summary,
               accomplishments,
               next_steps,
               dependencies,
               status_override
        FROM weekly_updates
        WHERE tenant_id::text = :tenant_id
          AND week_ending = :week_ending
        """,
        {"tenant_id": tenant_id, "week_ending": week_ending},
    )
