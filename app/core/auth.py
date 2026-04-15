from __future__ import annotations

from collections.abc import Mapping
from urllib.parse import urlsplit

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError

from app.core.config import load_auth_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


APP_NAME = "Impower AI"
_REQUIRED_AUTH_KEYS = ("client_id", "client_secret", "redirect_uri", "server_metadata_url", "cookie_secret")
_PLACEHOLDER_MARKERS = ("<", "your_", "changeme", "replace_me", "example")


def _mask_secret(value: str, unmasked: int = 4) -> str:
    if len(value) <= unmasked:
        return "*" * len(value)
    return ("*" * max(len(value) - unmasked, 0)) + value[-unmasked:]


def _build_suggested_auth_toml(auth: dict[str, str], fallback_base_url: str) -> str:
    redirect_uri = auth.get("redirect_uri") or f"{fallback_base_url}/oauth2callback"
    return "\n".join(
        [
            "[auth]",
            f'redirect_uri = "{redirect_uri}"',
            (
                f'cookie_secret = "{_mask_secret(auth["cookie_secret"])}"'
                if auth.get("cookie_secret")
                else 'cookie_secret = "<A_LONG_RANDOM_SECRET>"'
            ),
            "",
            "[auth.auth0]",
            f'client_id = "{auth.get("client_id") or "<YOUR_CLIENT_ID>"}"',
            f'client_secret = "{_mask_secret(auth["client_secret"]) if auth.get("client_secret") else "<YOUR_CLIENT_SECRET>"}"',
            (
                f'server_metadata_url = "{auth["server_metadata_url"]}"'
                if auth.get("server_metadata_url")
                else 'server_metadata_url = "https://<YOUR_DOMAIN>/.well-known/openid-configuration"'
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


def _validate_auth_config(auth: dict[str, str]) -> list[str]:
    missing_keys = [key for key in _REQUIRED_AUTH_KEYS if not str(auth.get(key, "")).strip()]
    if missing_keys:
        return [f"Missing required keys: {', '.join(missing_keys)}"]

    redirect_uri = str(auth.get("redirect_uri", "")).strip()
    metadata_url = str(auth.get("server_metadata_url", "")).strip()
    redirect_parsed = urlsplit(redirect_uri)
    metadata_parsed = urlsplit(metadata_url)

    issues: list[str] = []
    if not (redirect_parsed.scheme and redirect_parsed.netloc):
        issues.append("redirect_uri must be an absolute URL")
    if not (metadata_parsed.scheme and metadata_parsed.netloc):
        issues.append("server_metadata_url must be an absolute URL")
    return issues


def _validate_streamlit_secrets_shape() -> list[str]:
    """Ensure secrets are in Streamlit's provider-aware OIDC structure.

    `load_auth_config()` supports compatibility fallbacks (legacy `[auth0]` block,
    flattened keys, etc.) for diagnostics, but `st.login("auth0")` still reads the
    canonical `[auth]` + `[auth.auth0]` sections directly from `st.secrets`.
    """

    issues: list[str] = []
    try:
        auth_section = st.secrets.get("auth")
    except StreamlitSecretNotFoundError:
        return []
    if not isinstance(auth_section, Mapping):
        return [
            "Streamlit secrets must include an [auth] section (legacy [auth0]-only config is not enough)"
        ]

    provider_section = auth_section.get("auth0")
    top_level_client_id = str(auth_section.get("client_id", "")).strip()
    top_level_client_secret = str(auth_section.get("client_secret", "")).strip()

    if top_level_client_id or top_level_client_secret:
        issues.append(
            "Remove top-level [auth] client_id/client_secret and keep credentials only in [auth.auth0]; "
            "top-level [auth] credentials can trigger Auth0 'Failed Exchange: Unauthorized'"
        )

    if not isinstance(provider_section, Mapping):
        issues.append("Streamlit secrets must include an [auth.auth0] provider block")
        return issues

    redirect_uri_raw = str(auth_section.get("redirect_uri", ""))
    cookie_secret_raw = str(auth_section.get("cookie_secret", ""))
    client_id_raw = str(provider_section.get("client_id", ""))
    client_secret_raw = str(provider_section.get("client_secret", ""))
    metadata_raw = str(provider_section.get("server_metadata_url", ""))

    if not redirect_uri_raw.strip():
        issues.append("[auth].redirect_uri is required")
    if not cookie_secret_raw.strip():
        issues.append("[auth].cookie_secret is required")
    if not client_id_raw.strip():
        issues.append("[auth.auth0].client_id is required")
    if not client_secret_raw.strip():
        issues.append("[auth.auth0].client_secret is required")
    if not metadata_raw.strip():
        issues.append("[auth.auth0].server_metadata_url is required")

    fields_to_trim = {
        "[auth].redirect_uri": redirect_uri_raw,
        "[auth].cookie_secret": cookie_secret_raw,
        "[auth.auth0].client_id": client_id_raw,
        "[auth.auth0].client_secret": client_secret_raw,
        "[auth.auth0].server_metadata_url": metadata_raw,
    }
    for field_name, value in fields_to_trim.items():
        if value and value != value.strip():
            issues.append(f"{field_name} contains leading/trailing whitespace")

    fields_to_check_placeholder = {
        "[auth.auth0].client_id": client_id_raw.strip(),
        "[auth.auth0].client_secret": client_secret_raw.strip(),
    }
    for field_name, value in fields_to_check_placeholder.items():
        lowered = value.lower()
        if value and any(marker in lowered for marker in _PLACEHOLDER_MARKERS):
            issues.append(f"{field_name} appears to be a placeholder value")

    sensitive_fields = {
        "[auth.auth0].client_id": client_id_raw,
        "[auth.auth0].client_secret": client_secret_raw,
    }
    for field_name, value in sensitive_fields.items():
        if any(ch in value for ch in ("\n", "\r", "\t")):
            issues.append(f"{field_name} contains control characters")
    return issues


def login_with_auth0() -> None:
    auth = load_auth_config()
    auth_issues = _validate_auth_config(auth)
    auth_issues.extend(_validate_streamlit_secrets_shape())
    if auth_issues:
        st.error(
            "Authentication is not configured correctly. "
            + "; ".join(auth_issues)
            + "."
        )
        render_auth_troubleshooting_panel("; ".join(auth_issues))
        return

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
