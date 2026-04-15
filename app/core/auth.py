from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.core.config import load_auth_config, load_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


def _missing_auth_requirements() -> list[str]:
    auth = load_auth_config()
    missing: list[str] = []
    if not isinstance(auth, dict):
        return ["[auth] block"]

    if not auth.get("redirect_uri"):
        missing.append("[auth].redirect_uri")
    if not auth.get("cookie_secret"):
        missing.append("[auth].cookie_secret")

    named_provider_configs = {
        key: value
        for key, value in auth.items()
        if isinstance(key, str) and isinstance(value, dict)
    }
    auth_provider = load_config().auth_provider
    if auth_provider is None:
        inline_keys = ("client_id", "client_secret", "server_metadata_url")
        for key in inline_keys:
            if not auth.get(key):
                missing.append(f"[auth].{key}")
    else:
        provider_config = named_provider_configs.get(auth_provider, {})
        for key in ("client_id", "client_secret", "server_metadata_url"):
            if not provider_config.get(key):
                missing.append(f"[auth.{auth_provider}].{key}")

    return missing


def _legacy_auth0_hint() -> str | None:
    auth0 = st.secrets.get("auth0", {})
    if not isinstance(auth0, dict):
        return None

    has_legacy = bool(auth0.get("domain") and auth0.get("client_id") and auth0.get("client_secret"))
    if not has_legacy:
        return None

    return (
        "Detected legacy Auth0 secrets under `[auth0]`. Streamlit OIDC requires "
        "`[auth]` and `[auth.auth0]` in `.streamlit/secrets.toml` (including "
        "`server_metadata_url`, typically `https://<domain>/.well-known/openid-configuration`)."
    )


def _has_value(config: dict, key: str) -> bool:
    return bool(isinstance(config, dict) and config.get(key))


def _render_auth_diagnostics(error: Exception | None = None) -> None:
    auth = load_auth_config()
    named_provider_configs = {
        key: value
        for key, value in auth.items()
        if isinstance(key, str) and isinstance(value, dict)
    }

    auth_provider = load_config().auth_provider
    provider_config = named_provider_configs.get(auth_provider) if auth_provider else {}
    legacy_auth0 = st.secrets.get("auth0", {})

    rows = [
        {
            "check": "[auth] exists",
            "status": isinstance(auth, dict),
        },
        {
            "check": "[auth].redirect_uri set",
            "status": _has_value(auth, "redirect_uri"),
        },
        {
            "check": "[auth].cookie_secret set",
            "status": _has_value(auth, "cookie_secret"),
        },
        {
            "check": "provider resolved",
            "status": auth_provider is not None or (
                _has_value(auth, "client_id") and _has_value(auth, "client_secret")
            ),
            "details": auth_provider or "inline provider in [auth]",
        },
        {
            "check": "named providers under [auth]",
            "status": bool(named_provider_configs),
            "details": ", ".join(sorted(named_provider_configs)) or "none",
        },
        {
            "check": "legacy [auth0] block detected",
            "status": isinstance(legacy_auth0, dict) and bool(legacy_auth0),
            "details": "legacy config is ignored by Streamlit OIDC",
        },
    ]

    if auth_provider and isinstance(provider_config, dict):
        rows.extend(
            [
                {
                    "check": f"[auth.{auth_provider}].client_id set",
                    "status": _has_value(provider_config, "client_id"),
                },
                {
                    "check": f"[auth.{auth_provider}].client_secret set",
                    "status": _has_value(provider_config, "client_secret"),
                },
                {
                    "check": f"[auth.{auth_provider}].server_metadata_url set",
                    "status": _has_value(provider_config, "server_metadata_url"),
                },
            ]
        )

    with st.expander("Authentication troubleshooting", expanded=True):
        st.write(
            "Use these checks to validate whether this deployment has enough OIDC "
            "configuration for `st.login()` to work."
        )
        st.table(rows)

        if error is not None:
            st.code(f"StreamlitAuthError: {error}")

        st.caption("If you currently use `[auth0]`, migrate to this format:")
        st.code(
            """[auth]
redirect_uri = "https://YOUR-APP.streamlit.app/"
cookie_secret = "LONG_RANDOM_SECRET"

[auth.auth0]
client_id = "..."
client_secret = "..."
server_metadata_url = "https://YOUR_DOMAIN/.well-known/openid-configuration"
"""
        )


def ensure_authenticated_user() -> object:
    streamlit_user = getattr(st, "user", None)
    is_logged_in = bool(getattr(streamlit_user, "is_logged_in", False))

    if not is_logged_in:
        st.title("Executive Delivery Dashboard")
        st.caption("Production reporting platform")

        login_fn = getattr(st, "login", None)
        auth_provider = load_config().auth_provider
        missing_requirements = _missing_auth_requirements()
        auth_ready = not missing_requirements
        if not auth_ready:
            legacy_hint = _legacy_auth0_hint()
            if legacy_hint is not None and missing_requirements == ["[auth] block"]:
                st.warning(
                    "Authentication is partially configured. Missing required values: "
                    "[auth] block (legacy [auth0] settings were detected)."
                )
                st.info(legacy_hint)
            else:
                st.warning(
                    "Authentication is partially configured. Missing required values: "
                    + ", ".join(missing_requirements)
                )

        if callable(login_fn) and auth_provider:
            if st.button("Sign in", type="primary", disabled=not auth_ready):
                try:
                    login_fn(auth_provider)
                except StreamlitAuthError as exc:
                    st.info(
                        _legacy_auth0_hint()
                        or "Authentication is not configured for this deployment. "
                        "Configure credentials for an auth provider in "
                        "`.streamlit/secrets.toml`, then reload this app."
                    )
                    _render_auth_diagnostics(exc)
        elif callable(login_fn) and auth_provider is None:
            if st.button("Sign in", type="primary", disabled=not auth_ready):
                try:
                    login_fn()
                except StreamlitAuthError as exc:
                    st.info(
                        _legacy_auth0_hint()
                        or "Authentication is not configured for this deployment. "
                        "Configure credentials for an auth provider in "
                        "`.streamlit/secrets.toml`, then reload this app."
                    )
                    _render_auth_diagnostics(exc)
        else:
            st.info(
                _legacy_auth0_hint()
                or "Authentication is not configured for this deployment. "
                "Configure an auth provider, then reload this app."
            )
            _render_auth_diagnostics()

        st.stop()

    return streamlit_user


def load_user_context(streamlit_user: object) -> UserContext:
    user = User(
        provider="oidc",
        provider_sub=getattr(streamlit_user, "sub", "unknown"),
        email=getattr(streamlit_user, "email", None),
        display_name=getattr(streamlit_user, "name", "User"),
    )
    roles = getattr(streamlit_user, "roles", []) or ["client_viewer"]
    tenants = ["default"]
    return UserContext(user=user, role_codes=set(roles), tenant_slugs=tenants)
