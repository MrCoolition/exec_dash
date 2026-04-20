from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any, Iterator

from psycopg2.extras import RealDictCursor

from app.core.db import get_connection_pool

_PARAM_PATTERN = re.compile(r"(?<!:):([A-Za-z_][A-Za-z0-9_]*)")


def _to_psycopg2_query(query: str) -> str:
    return _PARAM_PATTERN.sub(r"%(\1)s", query)


@contextmanager
def connection() -> Iterator[Any]:
    """Open a pooled PostgreSQL connection with transaction semantics."""
    pool = get_connection_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(_to_psycopg2_query(query), params or {})
        rows = cursor.fetchall()
    return [dict(row) for row in rows]


def fetch_one(query: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
    with connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(_to_psycopg2_query(query), params or {})
        row = cursor.fetchone()
    return dict(row) if row else None


def execute(query: str, params: dict[str, Any] | None = None) -> None:
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(_to_psycopg2_query(query), params or {})


def execute_scalar(query: str, params: dict[str, Any] | None = None) -> Any:
    with connection() as conn, conn.cursor() as cursor:
        cursor.execute(_to_psycopg2_query(query), params or {})
        row = cursor.fetchone()
    return row[0] if row else None
