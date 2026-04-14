from __future__ import annotations

import streamlit as st

from app.core.config import load_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


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
                login_fn(auth_provider)
        else:
            st.info(
                "Authentication is not configured for this deployment. "
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
