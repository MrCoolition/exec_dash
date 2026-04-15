from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.models.pydantic_models import User
from app.services.user_context import UserContext


APP_NAME = "Impower AI"


def login_with_auth0() -> None:
    try:
        st.login("auth0")
    except StreamlitAuthError:
        st.error(
            "Authentication is not configured correctly. "
            "Please add valid [auth] / [auth0] credentials in Streamlit secrets."
        )


def sync_user_from_oidc() -> None:
    if not st.user.is_logged_in:
        st.session_state["authenticated"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = ""
        st.session_state["user_email"] = ""
        st.session_state["user_description"] = ""
        st.session_state["user_role"] = "user"
        return

    identity = st.user.to_dict()

    email = identity.get("email", "")
    name = identity.get("name") or identity.get("given_name") or email or "user"
    oidc_sub = identity.get("sub", email)

    st.session_state["authenticated"] = True
    st.session_state["user_id"] = oidc_sub
    st.session_state["username"] = name
    st.session_state["user_email"] = email
    st.session_state["user_description"] = ""
    st.session_state["user_role"] = "user"


def ensure_authenticated_user() -> object:
    sync_user_from_oidc()
    if not st.session_state.get("authenticated", False):
        st.title(APP_NAME)
        st.button("Login with Auth0", on_click=login_with_auth0, type="primary")
        st.stop()

    return type(
        "OidcUser",
        (),
        {
            "provider_sub": st.session_state.get("user_id") or "user",
            "email": st.session_state.get("user_email", ""),
            "display_name": st.session_state.get("username", "user"),
            "roles": st.session_state.get("user_role", "user"),
        },
    )()


def load_user_context(streamlit_user: object) -> UserContext:
    user = User(
        provider="auth0",
        provider_sub=getattr(streamlit_user, "provider_sub", "unknown"),
        email=getattr(streamlit_user, "email", None),
        display_name=getattr(streamlit_user, "display_name", "User"),
    )
    roles_raw = getattr(streamlit_user, "roles", "") or "user"
    roles = [role.strip() for role in str(roles_raw).split(",") if role.strip()]
    tenants = ["default"]
    return UserContext(user=user, role_codes=set(roles), tenant_slugs=tenants)
