from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.core.config import load_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


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


def ensure_authenticated_user() -> object:
    streamlit_user = getattr(st, "user", None)
    is_logged_in = bool(getattr(streamlit_user, "is_logged_in", False))

    if not is_logged_in:
        st.title("Executive Delivery Dashboard")
        st.caption("Production reporting platform")

        login_fn = getattr(st, "login", None)
        auth_provider = load_config().auth_provider
        if callable(login_fn) and auth_provider:
            if st.button("Sign in", type="primary"):
                try:
                    login_fn(auth_provider)
                except StreamlitAuthError:
                    st.info(
                        _legacy_auth0_hint()
                        or "Authentication is not configured for this deployment. "
                        "Configure credentials for an auth provider in "
                        "`.streamlit/secrets.toml`, then reload this app."
                    )
        elif callable(login_fn) and auth_provider is None:
            if st.button("Sign in", type="primary"):
                try:
                    login_fn()
                except StreamlitAuthError:
                    st.info(
                        _legacy_auth0_hint()
                        or "Authentication is not configured for this deployment. "
                        "Configure credentials for an auth provider in "
                        "`.streamlit/secrets.toml`, then reload this app."
                    )
        else:
            st.info(
                _legacy_auth0_hint()
                or "Authentication is not configured for this deployment. "
                "Configure an auth provider, then reload this app."
            )

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
