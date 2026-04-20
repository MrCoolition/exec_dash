from __future__ import annotations

from collections.abc import Iterable
import logging

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.models.pydantic_models import User
from app.services.user_context import UserContext


APP_NAME = "Impower AI"
_LOG = logging.getLogger(__name__)


_AUTH_SESSION_DEFAULTS: dict[str, object] = {
    "authenticated": False,
    "user_id": None,
    "username": "",
    "user_email": "",
    "user_description": "",
    "user_roles": ["user"],
}


def _as_roles(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [r.strip() for r in raw.split(",") if r.strip()]
    if isinstance(raw, Iterable):
        return [str(r).strip() for r in raw if str(r).strip()]
    return []


def _extract_roles(identity: dict) -> list[str]:
    direct = _as_roles(identity.get("roles"))
    if direct:
        return direct

    namespaced = [k for k in identity.keys() if k.endswith("/roles")]
    for key in namespaced:
        roles = _as_roles(identity.get(key))
        if roles:
            return roles

    app_meta = identity.get("app_metadata")
    if isinstance(app_meta, dict):
        meta_roles = _as_roles(app_meta.get("roles"))
        if meta_roles:
            return meta_roles

    return ["user"]


def login_with_auth0() -> None:
    try:
        st.login("auth0")
    except StreamlitAuthError:
        _LOG.exception("Auth0 login attempt failed")
        st.error("We couldn't complete sign in. Please try again or contact support.")


def clear_auth_session_state() -> None:
    for key, value in _AUTH_SESSION_DEFAULTS.items():
        st.session_state[key] = value

    st.session_state.pop("auth_callback_attempts", None)
    st.session_state.pop("auth_callback_marker", None)


def sync_user_from_oidc() -> None:
    if not st.user.is_logged_in:
        clear_auth_session_state()
        return

    identity = st.user.to_dict()
    email = identity.get("email", "")
    name = identity.get("name") or identity.get("given_name") or email or "user"
    oidc_sub = identity.get("sub", email)
    roles = _extract_roles(identity)

    st.session_state["authenticated"] = True
    st.session_state["user_id"] = oidc_sub
    st.session_state["username"] = name
    st.session_state["user_email"] = email
    st.session_state["user_description"] = ""
    st.session_state["user_roles"] = roles


def load_user_from_session() -> object:
    return type(
        "OidcUser",
        (),
        {
            "provider_sub": st.session_state.get("user_id") or "user",
            "email": st.session_state.get("user_email", ""),
            "display_name": st.session_state.get("username", "user"),
            "roles": st.session_state.get("user_roles", ["user"]),
        },
    )()


def load_user_context(streamlit_user: object) -> UserContext:
    user = User(
        provider="auth0",
        provider_sub=getattr(streamlit_user, "provider_sub", "unknown"),
        email=getattr(streamlit_user, "email", None),
        display_name=getattr(streamlit_user, "display_name", "User"),
    )
    roles_raw = getattr(streamlit_user, "roles", ["user"])
    roles = set(_as_roles(roles_raw) or ["user"])
    tenants = ["default"]
    return UserContext(user=user, role_codes=roles, tenant_slugs=tenants)
