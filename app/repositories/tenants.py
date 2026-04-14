from __future__ import annotations

from sqlalchemy import select

from app.core.db import db_session
from app.models.sqlalchemy_models import Tenant


def list_active_tenants() -> list[Tenant]:
    with db_session() as session:
        return list(session.scalars(select(Tenant).where(Tenant.is_active.is_(True))).all())
