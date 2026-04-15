from __future__ import annotations

import json
from collections.abc import Mapping
from urllib.parse import urlparse

import streamlit as st
from streamlit.errors import StreamlitAuthError

from app.core.config import load_auth_config
from app.models.pydantic_models import User
from app.services.user_context import UserContext


def _extract_identity_from_headers() -> tuple[dict[str, str], list[dict[str, str]]]:
    context = getattr(st, "context", None)
    headers = getattr(context, "headers", None) if context is not None else None

    diagnostics: list[dict[str, str]] = []
    if not headers:
        diagnostics.append(
            {
                "source": "request headers",
                "status": "missing",
                "details": "No request headers available from Streamlit context.",
            }
        )
        return {}, diagnostics

    # Streamlit headers object is case-insensitive, but normalize for safety.
    normalized = {str(key).lower(): str(value) for key, value in dict(headers).items()}

    email = (
        normalized.get("x-auth-request-email")
        or normalized.get("x-forwarded-email")
        or normalized.get("x-okta-email")
        or normalized.get("x-user-email")
    )
    display_name = (
        normalized.get("x-auth-request-user")
        or normalized.get("x-forwarded-user")
        or normalized.get("x-okta-user")
        or normalized.get("x-user-name")
    )
    provider_sub = (
        normalized.get("x-auth-request-sub")
        or normalized.get("x-forwarded-sub")
        or normalized.get("x-user-id")
    )

    # Optional Auth0/OpenID userinfo header (if your reverse proxy forwards it).
    raw_userinfo = normalized.get("x-auth0-userinfo")
    if raw_userinfo:
        try:
            userinfo = json.loads(raw_userinfo)
        except json.JSONDecodeError:
            diagnostics.append(
                {
                    "source": "x-auth0-userinfo",
                    "status": "invalid",
                    "details": "Header exists but is not valid JSON.",
                }
            )
        else:
            email = email or userinfo.get("email")
            display_name = display_name or userinfo.get("name")
            provider_sub = provider_sub or userinfo.get("sub")
            diagnostics.append(
                {
                    "source": "x-auth0-userinfo",
                    "status": "ok",
                    "details": "Parsed Auth0 userinfo JSON from header.",
                }
            )

    roles_raw = normalized.get("x-user-roles") or normalized.get("x-forwarded-roles")
    roles = [role.strip() for role in (roles_raw or "").split(",") if role.strip()]

    if email or provider_sub or display_name:
        diagnostics.append(
            {
                "source": "identity headers",
                "status": "ok",
                "details": "Found user identity headers from upstream auth proxy.",
            }
        )
        return {
            "email": email or "",
            "display_name": display_name or "",
            "provider_sub": provider_sub or email or "header-user",
            "roles": ",".join(roles),
        }, diagnostics

    diagnostics.append(
        {
            "source": "identity headers",
            "status": "missing",
            "details": "No identity headers found (email/sub/name).",
        }
    )
    return {}, diagnostics


def _extract_identity_from_streamlit_user() -> tuple[dict[str, str], list[dict[str, str]]]:
    user = getattr(st, "user", None)
    if user is None:
        return {}, [
            {
                "source": "Streamlit OIDC user",
                "status": "missing",
                "details": "`st.user` is unavailable in this runtime.",
            }
        ]

    is_logged_in = bool(getattr(user, "is_logged_in", False))
    if not is_logged_in:
        return {}, [
            {
                "source": "Streamlit OIDC user",
                "status": "missing",
                "details": "User is not logged in via Streamlit OIDC.",
            }
        ]

    email = str(getattr(user, "email", "") or "").strip()
    display_name = str(getattr(user, "name", "") or "").strip()
    provider_sub = str(getattr(user, "sub", "") or "").strip() or email

    if not provider_sub:
        return {}, [
            {
                "source": "Streamlit OIDC user",
                "status": "invalid",
                "details": "Logged-in user missing both subject and email.",
            }
        ]

    return {
        "email": email,
        "display_name": display_name or email or "User",
        "provider_sub": provider_sub,
        "roles": "",
    }, [
        {
            "source": "Streamlit OIDC user",
            "status": "ok",
            "details": "Using authenticated Streamlit OIDC user identity.",
        }
    ]


def _extract_identity_from_secrets() -> tuple[dict[str, str], list[dict[str, str]]]:
    identity = st.secrets.get("identity", {})
    if not isinstance(identity, Mapping) or not identity:
        return {}, [
            {
                "source": "[identity] secrets",
                "status": "missing",
                "details": "No fallback identity configured.",
            }
        ]
    identity = dict(identity)

    email = str(identity.get("email", "")).strip()
    provider_sub = str(identity.get("provider_sub", "")).strip() or email
    display_name = str(identity.get("display_name", "")).strip() or email
    roles_raw = str(identity.get("roles", "client_viewer"))
    roles = [role.strip() for role in roles_raw.split(",") if role.strip()]

    if not provider_sub:
        return {}, [
            {
                "source": "[identity] secrets",
                "status": "invalid",
                "details": "Missing both provider_sub and email.",
            }
        ]

    return {
        "email": email,
        "provider_sub": provider_sub,
        "display_name": display_name or "User",
        "roles": ",".join(roles),
    }, [
        {
            "source": "[identity] secrets",
            "status": "ok",
            "details": "Using configured fallback identity from secrets.",
        }
    ]


def _render_auth_troubleshooting(rows: list[dict[str, str]]) -> None:
    with st.expander("Authentication troubleshooting", expanded=True):
        st.write(
            "This app expects authentication to happen upstream (Okta/Auth0). "
            "If identity headers are missing, configure a temporary `[identity]` "
            "fallback in `.streamlit/secrets.toml` while troubleshooting."
        )
        st.table(rows)


def _oidc_login_readiness() -> tuple[bool, str]:
    auth = load_auth_config()
    required_fields = ("client_id", "client_secret", "server_metadata_url", "redirect_uri", "cookie_secret")
    missing = [field for field in required_fields if not str(auth.get(field, "")).strip()]
    if missing:
        missing_list = ", ".join(missing)
        return False, (
            "OIDC login is not available because Streamlit auth secrets are incomplete. "
            f"Missing required keys: {missing_list}."
        )

    metadata_url = str(auth.get("server_metadata_url", "")).strip()
    redirect_uri = str(auth.get("redirect_uri", "")).strip()

    metadata_parts = urlparse(metadata_url)
    if metadata_parts.scheme not in {"http", "https"} or not metadata_parts.netloc:
        return False, (
            "OIDC login is not available because `server_metadata_url` is invalid. "
            "Set it to a full URL like "
            "`https://<issuer>/.well-known/openid-configuration`."
        )
    if ".well-known/openid-configuration" not in metadata_parts.path:
        return False, (
            "OIDC login is not available because `server_metadata_url` must point to "
            "the OpenID configuration endpoint ending in `/.well-known/openid-configuration`."
        )

    redirect_parts = urlparse(redirect_uri)
    if redirect_parts.scheme not in {"http", "https"} or not redirect_parts.netloc:
        return False, (
            "OIDC login is not available because `redirect_uri` is invalid. "
            "Set it to a full URL like `https://<app-host>/oauth2callback`."
        )
    if not redirect_parts.path.endswith("/oauth2callback"):
        return False, (
            "OIDC login is not available because `redirect_uri` should end with "
            "`/oauth2callback` for Streamlit OIDC."
        )
    return True, ""


def ensure_authenticated_user() -> object:
    header_identity, header_rows = _extract_identity_from_headers()
    if header_identity:
        return type("HeaderUser", (), header_identity)()

    oidc_identity, oidc_rows = _extract_identity_from_streamlit_user()
    if oidc_identity:
        st.info("Using Streamlit OIDC identity because upstream auth headers are unavailable.")
        _render_auth_troubleshooting(header_rows + oidc_rows)
        return type("OidcUser", (), oidc_identity)()

    secrets_identity, secrets_rows = _extract_identity_from_secrets()
    if secrets_identity:
        st.info("Using fallback identity from secrets because auth headers are unavailable.")
        _render_auth_troubleshooting(header_rows + oidc_rows + secrets_rows)
        return type("SecretsUser", (), secrets_identity)()

    st.title("Executive Delivery Dashboard")
    st.error("Authentication identity was not provided by the Okta/Auth0 upstream proxy.")
    st.write("If OIDC is configured in Streamlit secrets, use the login control below and retry.")
    oidc_ready, oidc_reason = _oidc_login_readiness()
    if not oidc_ready:
        st.warning(oidc_reason)
    if st.button("Log in with OIDC", type="primary", disabled=not oidc_ready):
        try:
            st.login()
        except StreamlitAuthError as exc:
            st.error("OIDC login could not start because Streamlit auth secrets are incomplete.")
            st.caption(f"Details: {exc}")
    _render_auth_troubleshooting(header_rows + oidc_rows + secrets_rows)
    st.stop()


def load_user_context(streamlit_user: object) -> UserContext:
    user = User(
        provider="okta-auth0",
        provider_sub=getattr(streamlit_user, "provider_sub", "unknown"),
        email=getattr(streamlit_user, "email", None),
        display_name=getattr(streamlit_user, "display_name", "User"),
    )
    roles_raw = getattr(streamlit_user, "roles", "") or "client_viewer"
    roles = [role.strip() for role in str(roles_raw).split(",") if role.strip()]
    tenants = ["default"]
    return UserContext(user=user, role_codes=set(roles), tenant_slugs=tenants)
