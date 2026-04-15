from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.db import get_engine


@contextmanager
def connection() -> Connection:
    """Open a database connection with transaction semantics."""
    with get_engine().begin() as conn:
        yield conn


def fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(text(query), params or {}).mappings().all()
        return [dict(row) for row in rows]


def fetch_one(query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with get_engine().connect() as conn:
        row = conn.execute(text(query), params or {}).mappings().first()
        return dict(row) if row else None


def execute(query: str, params: dict[str, Any] | None = None) -> None:
    with connection() as conn:
        conn.execute(text(query), params or {})
