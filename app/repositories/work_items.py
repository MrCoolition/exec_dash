from __future__ import annotations

from sqlalchemy import func, select

from app.core.db import db_session
from app.models.sqlalchemy_models import WorkItemCurrent


def count_by_state() -> list[tuple[str, int]]:
    with db_session() as session:
        rows = session.execute(
            select(WorkItemCurrent.state, func.count()).group_by(WorkItemCurrent.state)
        ).all()
        return [(r[0] or "Unknown", r[1]) for r in rows]
