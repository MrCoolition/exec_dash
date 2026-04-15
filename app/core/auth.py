from __future__ import annotations

from urllib.parse import urlsplit

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.core.config import load_auth_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


APP_NAME = "Impower AI"
_REQUIRED_AUTH_KEYS = ("client_id", "client_secret", "redirect_uri", "server_metadata_url", "cookie_secret")


def _mask_secret(value: str, unmasked: int = 4) -> str:
    if len(value) <= unmasked:
        return "*" * len(value)
    return ("*" * max(len(value) - unmasked, 0)) + value[-unmasked:]


def _build_suggested_auth_toml(auth: dict[str, str], fallback_base_url: str) -> str:
    redirect_uri = auth.get("redirect_uri") or f"{fallback_base_url}/oauth2callback"
    return "\n".join(
        [
            "[auth]",
            f'client_id = "{auth.get("client_id") or "<YOUR_CLIENT_ID>"}"',
            f'client_secret = "{_mask_secret(auth["client_secret"]) if auth.get("client_secret") else "<YOUR_CLIENT_SECRET>"}"',
            f'redirect_uri = "{redirect_uri}"',
            (
                f'server_metadata_url = "{auth["server_metadata_url"]}"'
                if auth.get("server_metadata_url")
                else 'server_metadata_url = "https://<YOUR_DOMAIN>/.well-known/openid-configuration"'
            ),
            (
                f'cookie_secret = "{_mask_secret(auth["cookie_secret"])}"'
                if auth.get("cookie_secret")
                else 'cookie_secret = "<A_LONG_RANDOM_SECRET>"'
            ),
        ]
    )


def render_auth_troubleshooting_panel(error_detail: str | None = None) -> None:
    auth = load_auth_config()
    missing_keys = [key for key in _REQUIRED_AUTH_KEYS if not auth.get(key)]
    redirect_uri = str(auth.get("redirect_uri") or "").strip()

    app_base_url = "https://exec-dash.streamlit.app"
    if redirect_uri:
        parsed = urlsplit(redirect_uri)
        if parsed.scheme and parsed.netloc:
            app_base_url = f"{parsed.scheme}://{parsed.netloc}"

    st.subheader("Authentication Self-Troubleshooting")
    if missing_keys:
        st.error(
            "Root cause: Streamlit OIDC credentials are incomplete. "
            f"Missing keys: {', '.join(missing_keys)}."
        )
        st.info("Remedy: Add the missing keys in app secrets, save, and restart/redeploy the app.")
    else:
        st.warning(
            "Root cause is likely a provider-side mismatch (callback URL / logout URL / web origin) "
            "or a stale secret value."
        )
        st.info("Remedy: Compare the values below with your Auth0 application settings and update any mismatch.")

    if error_detail:
        st.caption(f"Last login error: {error_detail}")

    st.markdown("#### Configuration checks")
    for key in _REQUIRED_AUTH_KEYS:
        value = auth.get(key)
        if value:
            st.write(f"✅ `{key}` is configured")
        else:
            st.write(f"❌ `{key}` is missing")

    st.markdown("#### Effective auth settings (masked)")
    st.code(_build_suggested_auth_toml(auth, app_base_url), language="toml")

    st.markdown("#### Auth0 dashboard values to verify")
    st.code(
        "\n".join(
            [
                f"Allowed Callback URLs: {app_base_url}/oauth2callback",
                f"Allowed Logout URLs: {app_base_url}",
                f"Allowed Web Origins: {app_base_url}",
            ]
        ),
        language="text",
    )


def login_with_auth0() -> None:
    try:
        st.login("auth0")
    except StreamlitAuthError as exc:
        st.error(
            "Authentication is not configured correctly. "
            "Please add valid [auth] / [auth0] credentials in Streamlit secrets."
        )
        render_auth_troubleshooting_panel(str(exc))


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
