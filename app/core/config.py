from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import quote_plus, urlparse

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


@dataclass(frozen=True)
class AuthValidationResult:
    is_valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    canonical: dict[str, str]


def _coerce_mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def _as_clean_str(value: object) -> str:
    return str(value or "").strip()

def _looks_like_placeholder(value: str) -> bool:
    if not value:
        return False
    normalized = value.strip()
    upper = normalized.upper()
    placeholder_tokens = ("YOUR_", "CHANGEME", "REPLACE_ME", "REPLACE-WITH", "<LONG_RANDOM_SECRET>")
    return any(token in upper for token in placeholder_tokens)


def load_canonical_auth_secrets(raw_secrets: Mapping[str, object] | None = None) -> dict[str, str]:
    secrets = raw_secrets if raw_secrets is not None else st.secrets
    auth = _coerce_mapping(secrets.get("auth"))
    provider = _coerce_mapping(auth.get("auth0"))

    return {
        "redirect_uri": _as_clean_str(auth.get("redirect_uri")),
        "cookie_secret": _as_clean_str(auth.get("cookie_secret")),
        "client_id": _as_clean_str(provider.get("client_id")),
        "client_secret": _as_clean_str(provider.get("client_secret")),
        "server_metadata_url": _as_clean_str(provider.get("server_metadata_url")),
    }


def validate_canonical_auth_config(raw_secrets: Mapping[str, object] | None = None) -> AuthValidationResult:
    secrets = raw_secrets if raw_secrets is not None else st.secrets
    canonical = load_canonical_auth_secrets(secrets)
    errors: list[str] = []
    warnings: list[str] = []

    for key, value in canonical.items():
        if not value:
            errors.append(f"Missing required secret: auth{'.auth0' if key in {'client_id', 'client_secret', 'server_metadata_url'} else ''}.{key}")

    sensitive_fields = ("cookie_secret", "client_id", "client_secret")
    for key in sensitive_fields:
        value = canonical.get(key, "")
        if value and _looks_like_placeholder(value):
            message = (
                f"auth{'.auth0' if key in {'client_id', 'client_secret'} else ''}.{key} appears to be a placeholder; set the real secret value."
            )
            if key == "cookie_secret":
                warnings.append(message)
            else:
                errors.append(message)

    if canonical["client_secret"] and len(canonical["client_secret"]) < 12:
        errors.append("auth.auth0.client_secret appears too short; verify you copied the full Auth0 client secret.")

    redirect_uri = canonical["redirect_uri"]
    if redirect_uri:
        parsed = urlparse(redirect_uri)
        if not parsed.scheme or not parsed.netloc:
            errors.append("auth.redirect_uri must be an absolute URL.")
        if not parsed.path.endswith("/oauth2callback"):
            errors.append("auth.redirect_uri must end with /oauth2callback.")
        disallowed_fragments = ("/~+/", "/~/", "/pages/", "/+/", "~+")
        if any(fragment in parsed.path for fragment in disallowed_fragments):
            errors.append("auth.redirect_uri must target the app root callback path, not a multipage route.")

    metadata_url = canonical["server_metadata_url"]
    if metadata_url:
        parsed_metadata = urlparse(metadata_url)
        if not parsed_metadata.scheme or not parsed_metadata.netloc:
            errors.append("auth.auth0.server_metadata_url must be an absolute URL.")
        if not metadata_url.endswith("/.well-known/openid-configuration"):
            errors.append(
                "auth.auth0.server_metadata_url must be a full well-known URL ending with /.well-known/openid-configuration."
            )

    legacy_auth0 = _coerce_mapping(secrets.get("auth0"))
    if legacy_auth0 and not _coerce_mapping(secrets.get("auth")):
        warnings.append("Legacy [auth0] block detected; runtime auth requires canonical [auth] and [auth.auth0] secrets.")

    return AuthValidationResult(
        is_valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        canonical=canonical,
    )


def load_auth_compat_diagnostics(raw_secrets: Mapping[str, object] | None = None) -> dict[str, object]:
    """Optional human-facing diagnostics for legacy auth secret shapes."""
    secrets = raw_secrets if raw_secrets is not None else st.secrets
    legacy_auth0 = _coerce_mapping(secrets.get("auth0"))
    auth = _coerce_mapping(secrets.get("auth"))

    alias_fields = tuple(
        key
        for key in ("domain", "redirectURL", "callback_url", "redirect uri")
        if key in auth or key in legacy_auth0
    )
    return {
        "has_legacy_auth0_block": bool(legacy_auth0),
        "uses_legacy_alias_fields": alias_fields,
    }


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
