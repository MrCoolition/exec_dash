from __future__ import annotations

from dataclasses import dataclass

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
    return AppConfig(
        auth_provider=auth.get("provider", "auth0"),
        database=DatabaseConfig(
            url=db.get("url", "sqlite+pysqlite:///./local.db"),
            sslmode=db.get("sslmode", "verify-ca"),
            ca_pem=aiven.get("ca_pem"),
        ),
        ado=AdoConfig(
            organization=ado.get("organization", ""),
            pat=ado.get("pat", ""),
            api_version=ado.get("api_version", "7.1"),
        ),
    )
