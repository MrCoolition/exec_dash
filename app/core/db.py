from __future__ import annotations

import tempfile
from urllib.parse import unquote, urlparse

from psycopg2.pool import ThreadedConnectionPool

from app.core.cache import cache_resource
from app.core.config import load_config


def _pool_kwargs_from_config() -> dict[str, object]:
    cfg = load_config().database
    parsed = urlparse(cfg.url.strip())

    if parsed.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError(
            "Only PostgreSQL URLs are supported. Configure st.secrets.database.url as postgresql://..."
        )

    kwargs: dict[str, object] = {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "dbname": (parsed.path or "/").lstrip("/"),
        "sslmode": cfg.sslmode,
    }

    if cfg.ca_pem:
        ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
        ca_file.write(cfg.ca_pem.encode("utf-8"))
        ca_file.flush()
        kwargs["sslrootcert"] = ca_file.name

    return kwargs


@cache_resource
def get_connection_pool() -> ThreadedConnectionPool:
    kwargs = _pool_kwargs_from_config()
    return ThreadedConnectionPool(minconn=1, maxconn=10, **kwargs)


def init_engine() -> ThreadedConnectionPool:
    return get_connection_pool()
