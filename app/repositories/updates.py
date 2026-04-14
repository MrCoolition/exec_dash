from __future__ import annotations

from datetime import date

from sqlalchemy import select

from app.core.db import db_session
from app.models.sqlalchemy_models import WeeklyUpdate


def get_weekly_update(tenant_id: str, week_ending: date) -> WeeklyUpdate | None:
    with db_session() as session:
        return session.scalar(
            select(WeeklyUpdate).where(
                WeeklyUpdate.tenant_id == tenant_id,
                WeeklyUpdate.week_ending == week_ending,
            )
        )
