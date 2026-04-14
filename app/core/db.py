from __future__ import annotations

import tempfile
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.cache import cache_resource
from app.core.config import load_config


@cache_resource
def get_engine() -> Engine:
    cfg = load_config().database
    connect_args = {}
    if cfg.ca_pem:
        ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
        ca_file.write(cfg.ca_pem.encode("utf-8"))
        ca_file.flush()
        connect_args = {
            "sslmode": cfg.sslmode,
            "sslrootcert": ca_file.name,
        }
    return create_engine(cfg.url, pool_pre_ping=True, connect_args=connect_args)


def init_engine() -> Engine:
    return get_engine()


@cache_resource
def _session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


@contextmanager
def db_session() -> Session:
    session = _session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
