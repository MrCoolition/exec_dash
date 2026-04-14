from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

import streamlit as st


@dataclass(frozen=True)
class DatabaseConfig:
    url: str
    sslmode: str = "verify-ca"
    ca_pem: str | None = None


@dataclass(frozen=True)
class AdoConfig:
    organization: str
    pat: str
    api_version: str = "7.1"


@dataclass(frozen=True)
class AppConfig:
    auth_provider: str
    database: DatabaseConfig
    ado: AdoConfig


def load_config() -> AppConfig:
    db = st.secrets.get("database", {})
    aiven = st.secrets.get("aiven", {})
    ado = st.secrets.get("azure_devops", {})
    auth = st.secrets.get("auth", {})

    database_url = db.get("url")
    if not database_url and db.get("AIVEN_HOST"):
        user = quote_plus(str(db.get("AIVEN_USER", "")))
        password = quote_plus(str(db.get("AIVEN_PASSWORD", "")))
        host = db.get("AIVEN_HOST", "")
        port = db.get("AIVEN_PORT", "5432")
        name = db.get("AIVEN_DB", "")
        database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

    auth_provider = auth.get("provider")
    if not auth_provider and st.secrets.get("auth0"):
        auth_provider = "auth0"

    sslmode = db.get("sslmode", "verify-ca")
    if db.get("AIVEN_HOST") and not db.get("sslmode"):
        sslmode = "require"

    return AppConfig(
        auth_provider=auth_provider or "auth0",
        database=DatabaseConfig(
            url=database_url or "sqlite+pysqlite:///./local.db",
            sslmode=sslmode,
            ca_pem=db.get("AIVEN_CA_PEM") or aiven.get("ca_pem"),
        ),
        ado=AdoConfig(
            organization=ado.get("organization", ""),
            pat=ado.get("pat", ""),
            api_version=ado.get("api_version", "7.1"),
        ),
    )
