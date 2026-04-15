from __future__ import annotations

from dataclasses import dataclass
import tomllib
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
    auth_provider: str | None
    database: DatabaseConfig
    ado: AdoConfig


def _parse_auth_from_raw_string(raw: str) -> dict:
    content = raw.strip()
    if not content:
        return {}

    # Some deploy environments inject TOML as a single-line string with escaped
    # newlines (e.g. "[auth]\\nclient_id = ..."). Decode that shape first.
    if "\\n" in content:
        content = content.replace("\\n", "\n")

    parse_candidates = [content]
    if "[auth]" not in content:
        parse_candidates.append(f"[auth]\n{content}")

    for candidate in parse_candidates:
        try:
            parsed = tomllib.loads(candidate)
        except tomllib.TOMLDecodeError:
            continue

        auth = parsed.get("auth")
        if isinstance(auth, dict):
            return auth

    return {}


def load_auth_config() -> dict:
    auth = st.secrets.get("auth", {})
    resolved: dict
    if isinstance(auth, dict):
        resolved = dict(auth)
    elif isinstance(auth, str):
        resolved = _parse_auth_from_raw_string(auth)
    else:
        resolved = {}

    # Backward-compatible Auth0 shorthand.
    domain = resolved.get("domain")
    if domain and not resolved.get("server_metadata_url"):
        normalized_domain = str(domain).strip().rstrip("/")
        if normalized_domain:
            if normalized_domain.startswith(("http://", "https://")):
                base = normalized_domain
            else:
                base = f"https://{normalized_domain}"
            resolved["server_metadata_url"] = f"{base}/.well-known/openid-configuration"

    # Streamlit OIDC needs cookie_secret; use an explicit value when possible,
    # but keep legacy configs operable by falling back to client_secret.
    if not resolved.get("cookie_secret") and resolved.get("client_secret"):
        resolved["cookie_secret"] = resolved["client_secret"]

    return resolved


def _resolve_auth_provider(auth: dict) -> str | None:
    provider = auth.get("provider")
    if provider:
        return str(provider)

    # If auth credentials are at the top level of [auth], st.login() should
    # be called without a provider argument.
    if auth.get("client_id") and auth.get("client_secret"):
        return None

    # For named providers (e.g. [auth.auth0]), infer provider when exactly one
    # is configured.
    named_providers = [
        key
        for key, value in auth.items()
        if isinstance(value, dict)
        and value.get("client_id")
        and value.get("client_secret")
    ]
    if len(named_providers) == 1:
        return named_providers[0]

    return None


def load_config() -> AppConfig:
    db = st.secrets.get("database", {})
    aiven = st.secrets.get("aiven", {})
    ado = st.secrets.get("azure_devops", {})
    auth = load_auth_config()

    database_url = db.get("url")
    if not database_url and db.get("AIVEN_HOST"):
        user = quote_plus(str(db.get("AIVEN_USER", "")))
        password = quote_plus(str(db.get("AIVEN_PASSWORD", "")))
        host = db.get("AIVEN_HOST", "")
        port = db.get("AIVEN_PORT", "5432")
        name = db.get("AIVEN_DB", "")
        database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

    auth_provider = _resolve_auth_provider(auth)

    sslmode = db.get("sslmode", "verify-ca")
    if db.get("AIVEN_HOST") and not db.get("sslmode"):
        sslmode = "require"

    return AppConfig(
        auth_provider=auth_provider,
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
