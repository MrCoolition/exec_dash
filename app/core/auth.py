from __future__ import annotations

import streamlit as st

from app.core.config import load_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


def ensure_authenticated_user() -> object:
    if not st.user.is_logged_in:
        st.title("Executive Delivery Dashboard")
        st.caption("Production reporting platform")
        if st.button("Sign in", type="primary"):
            st.login(load_config().auth_provider)
        st.stop()
    return st.user


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
