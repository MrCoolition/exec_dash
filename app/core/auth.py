from __future__ import annotations

import json

import streamlit as st

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


def _extract_identity_from_secrets() -> tuple[dict[str, str], list[dict[str, str]]]:
    identity = st.secrets.get("identity", {})
    if not isinstance(identity, dict) or not identity:
        return {}, [
            {
                "source": "[identity] secrets",
                "status": "missing",
                "details": "No fallback identity configured.",
            }
        ]

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


def ensure_authenticated_user() -> object:
    header_identity, header_rows = _extract_identity_from_headers()
    if header_identity:
        return type("HeaderUser", (), header_identity)()

    secrets_identity, secrets_rows = _extract_identity_from_secrets()
    if secrets_identity:
        st.info("Using fallback identity from secrets because auth headers are unavailable.")
        _render_auth_troubleshooting(header_rows + secrets_rows)
        return type("SecretsUser", (), secrets_identity)()

    st.title("Executive Delivery Dashboard")
    st.error("Authentication identity was not provided by the Okta/Auth0 upstream proxy.")
    _render_auth_troubleshooting(header_rows + secrets_rows)
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
