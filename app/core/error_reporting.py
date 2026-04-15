from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import traceback

import streamlit as st

from app.core.config import load_auth_config, load_config


def _safe_mask(value: str | None) -> str:
    if not value:
        return "<missing>"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def _classify_root_cause(exc: Exception) -> str:
    message = str(exc).lower()
    if any(token in message for token in ("auth", "oidc", "oauth", "token", "login")):
        return "Authentication or OIDC provider configuration mismatch"
    if any(token in message for token in ("connection refused", "could not translate host", "ssl", "password authentication failed", "postgres", "database", "psycopg")):
        return "Database connectivity or credentials issue"
    if any(token in message for token in ("permission", "forbidden", "unauthorized")):
        return "Permission or role mapping issue"
    if any(token in message for token in ("keyerror", "attributeerror", "none")):
        return "Missing required application state or malformed upstream payload"
    return "Unhandled application exception (see traceback and diagnostics below)"


def _secrets_shape() -> dict[str, str]:
    try:
        auth_section = st.secrets.get("auth")
    except Exception:
        auth_section = None

    auth_block_present = isinstance(auth_section, Mapping)
    auth0_block_present = isinstance(auth_section.get("auth0"), Mapping) if auth_block_present else False
    return {
        "has_[auth]": "yes" if auth_block_present else "no",
        "has_[auth.auth0]": "yes" if auth0_block_present else "no",
    }


def _build_runtime_snapshot() -> dict[str, str]:
    auth = load_auth_config()
    cfg = load_config()

    db_url = cfg.database.url
    if "://" in db_url:
        db_scheme = db_url.split("://", 1)[0]
    else:
        db_scheme = "unknown"

    snapshot = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "db_scheme": db_scheme,
        "db_sslmode": cfg.database.sslmode,
        "db_ca_present": "yes" if bool(cfg.database.ca_pem) else "no",
        "auth_redirect_uri": str(auth.get("redirect_uri") or "<missing>"),
        "auth_metadata_url": str(auth.get("server_metadata_url") or "<missing>"),
        "auth_client_id": _safe_mask(str(auth.get("client_id") or "")),
        "auth_cookie_secret_present": "yes" if bool(auth.get("cookie_secret")) else "no",
    }
    snapshot.update(_secrets_shape())
    return snapshot


def render_internal_error(exc: Exception, context: str) -> None:
    st.error("Internal error encountered. Self-troubleshooting details are shown below.")

    root_cause_guess = _classify_root_cause(exc)
    st.markdown("### Root-cause isolation")
    st.write(f"**Likely root cause:** {root_cause_guess}")
    st.write(f"**Failure context:** {context}")

    st.markdown("### Runtime diagnostics")
    st.table(_build_runtime_snapshot())

    st.markdown("### Exception details")
    st.code(
        "\n".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        ),
        language="text",
    )

    st.markdown("### Next actions")
    st.write(
        "1) Verify auth redirect/callback settings exactly match the running URL. "
        "2) Validate DB host, credentials, and SSL settings. "
        "3) Re-run after updating secrets to confirm whether the root cause changed."
    )
