from __future__ import annotations

from collections.abc import Mapping
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
    if isinstance(auth, Mapping):
        resolved = dict(auth)
    elif isinstance(auth, str):
        resolved = _parse_auth_from_raw_string(auth)
    else:
        resolved = {}

    # Streamlit's provider-aware OIDC shape nests credentials under
    # [auth.<provider>] (for this app: [auth.auth0]).
    provider_block = resolved.get("auth0", {})
    if isinstance(provider_block, Mapping):
        if not resolved.get("client_id") and provider_block.get("client_id"):
            resolved["client_id"] = provider_block["client_id"]
        if not resolved.get("client_secret") and provider_block.get("client_secret"):
            resolved["client_secret"] = provider_block["client_secret"]
        if not resolved.get("server_metadata_url") and provider_block.get("server_metadata_url"):
            resolved["server_metadata_url"] = provider_block["server_metadata_url"]
        if not resolved.get("domain") and provider_block.get("domain"):
            resolved["domain"] = provider_block["domain"]

    # Legacy Auth0 block compatibility:
    # map [auth0] into the Streamlit [auth] schema when [auth] is missing or
    # partially configured.
    legacy_auth0 = st.secrets.get("auth0", {})
    if isinstance(legacy_auth0, Mapping) and legacy_auth0:
        if not resolved.get("redirect_uri"):
            legacy_redirect = (
                legacy_auth0.get("redirect_uri")
                or legacy_auth0.get("callback_url")
                or legacy_auth0.get("redirectURL")
            )
            if legacy_redirect:
                resolved["redirect_uri"] = legacy_redirect

        if not resolved.get("client_id") and legacy_auth0.get("client_id"):
            resolved["client_id"] = legacy_auth0["client_id"]
        if not resolved.get("client_secret") and legacy_auth0.get("client_secret"):
            resolved["client_secret"] = legacy_auth0["client_secret"]

        if not resolved.get("server_metadata_url") and legacy_auth0.get("domain"):
            resolved["domain"] = legacy_auth0["domain"]

    # Backward-compatible shorthand for OIDC metadata discovery URL.
    # Accept common keys used across Auth0/Okta/OIDC samples.
    metadata_source = (
        resolved.get("server_metadata_url")
        or resolved.get("issuer")
        or resolved.get("issuer_url")
        or resolved.get("authority")
        or resolved.get("authority_url")
        or resolved.get("domain")
    )
    if metadata_source and not resolved.get("server_metadata_url"):
        normalized_source = str(metadata_source).strip().rstrip("/")
        if normalized_source:
            if normalized_source.startswith(("http://", "https://")):
                base = normalized_source
            else:
                base = f"https://{normalized_source}"
            if base.endswith("/.well-known/openid-configuration"):
                resolved["server_metadata_url"] = base
            else:
                resolved["server_metadata_url"] = f"{base}/.well-known/openid-configuration"

    # Streamlit OIDC needs cookie_secret; use an explicit value when possible,
    # then database.NOOKIE_PASS, and finally client_secret to keep legacy
    # deployments operable.
    if not resolved.get("cookie_secret"):
        db = st.secrets.get("database", {})
        if isinstance(db, Mapping) and db.get("NOOKIE_PASS"):
            resolved["cookie_secret"] = db["NOOKIE_PASS"]
    if not resolved.get("cookie_secret") and resolved.get("client_secret"):
        resolved["cookie_secret"] = resolved["client_secret"]

    return resolved



def load_config() -> AppConfig:
    db = st.secrets.get("database", {})
    aiven = st.secrets.get("aiven", {})
    ado = st.secrets.get("azure_devops", {})
    database_url = db.get("url")
    if not database_url and db.get("AIVEN_HOST"):
        user = quote_plus(str(db.get("AIVEN_USER", "")))
        password = quote_plus(str(db.get("AIVEN_PASSWORD", "")))
        host = db.get("AIVEN_HOST", "")
        port = db.get("AIVEN_PORT", "5432")
        name = db.get("AIVEN_DB", "")
        database_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"

    sslmode = db.get("sslmode", "verify-ca")
    if db.get("AIVEN_HOST") and not db.get("sslmode"):
        sslmode = "require"

    return AppConfig(
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
