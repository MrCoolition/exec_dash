from __future__ import annotations

from sqlalchemy import select

from app.core.db import db_session
from app.models.sqlalchemy_models import User


def upsert_user(provider: str, provider_sub: str, email: str | None, display_name: str | None) -> User:
    with db_session() as session:
        user = session.scalar(select(User).where(User.provider_sub == provider_sub))
        if user is None:
            user = User(provider=provider, provider_sub=provider_sub, email=email, display_name=display_name)
            session.add(user)
            session.flush()
        else:
            user.email = email
            user.display_name = display_name
        return user
