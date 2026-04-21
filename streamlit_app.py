from __future__ import annotations

import warnings
from collections.abc import Mapping, MutableMapping
from urllib.parse import urlparse

warnings.filterwarnings(
    "ignore",
    message=r"authlib\.jose module is deprecated, please use joserfc instead\..*",
    category=DeprecationWarning,
)

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError

from app.core.auth import (
    APP_NAME,
    clear_auth_session_state,
    load_user_context,
    load_user_from_session,
    login_with_auth0,
    sync_user_from_oidc,
)
from app.core.config import AuthValidationResult, validate_canonical_auth_config
from app.core.db import init_engine
from app.core.error_reporting import render_internal_error
from app.core.logging import configure_logging
from app.ui.layout import configure_page
from app.ui.pages import build_pages

st.set_page_config(page_title=APP_NAME, page_icon="🧊", layout="wide", initial_sidebar_state="expanded")

_CALLBACK_ATTEMPTS_KEY = "auth_callback_attempts"
_CALLBACK_MARKER_KEY = "auth_callback_marker"


def safe_is_logged_in() -> bool:
    if st.session_state.get("force_logged_out", False):
        return False
    try:
        return bool(st.user.is_logged_in)
    except (StreamlitAuthError, StreamlitSecretNotFoundError, Exception):
        return False


def _record_callback_failure(session_state: MutableMapping[str, object], query_params: Mapping[str, object]) -> int:
    callback_code = str(query_params.get("code", ""))
    callback_error = str(query_params.get("error", ""))
    callback_state = str(query_params.get("state", ""))
    has_callback = bool(callback_code or callback_error)
    if not has_callback:
        return int(session_state.get(_CALLBACK_ATTEMPTS_KEY, 0))

    marker = "|".join((callback_code, callback_error, callback_state))
    if session_state.get(_CALLBACK_MARKER_KEY) != marker:
        session_state[_CALLBACK_MARKER_KEY] = marker
        session_state[_CALLBACK_ATTEMPTS_KEY] = int(session_state.get(_CALLBACK_ATTEMPTS_KEY, 0)) + 1

    return int(session_state.get(_CALLBACK_ATTEMPTS_KEY, 0))


def _configured_redirect_base(redirect_uri: str) -> str:
    parsed = urlparse(redirect_uri)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def _runtime_auth_diagnostics(validation: AuthValidationResult) -> tuple[list[str], bool, str, str]:
    callback_failed = bool(st.query_params.get("code") or st.query_params.get("error")) and not safe_is_logged_in()

    try:
        browser_url = _as_text(st.context.url)
    except Exception:
        browser_url = ""
    browser_base = ""
    if browser_url:
        parsed = urlparse(browser_url)
        if parsed.scheme and parsed.netloc:
            browser_base = f"{parsed.scheme}://{parsed.netloc}"

    configured_base = _configured_redirect_base(validation.canonical.get("redirect_uri", ""))
    return list(validation.errors), callback_failed, configured_base, browser_base


def _as_text(value: object) -> str:
    return str(value or "").strip()


def _render_auth_config_error(validation: AuthValidationResult) -> None:
    st.title(APP_NAME)
    st.error("Auth configuration is invalid. Update Streamlit secrets before attempting login.")
    for issue in validation.errors:
        st.markdown(f"- {issue}")
    for warning in validation.warnings:
        st.warning(warning)


def _logout() -> None:
    clear_auth_session_state()
    st.session_state["force_logged_out"] = True
    st.query_params.clear()
    st.rerun()


def render_clean_login_screen(validation: AuthValidationResult) -> None:
    st.title(APP_NAME)
    st.caption("Executive reporting command center")

    errors, callback_failed, configured_base, browser_base = _runtime_auth_diagnostics(validation)
    callback_attempts = _record_callback_failure(st.session_state, st.query_params)

    if errors:
        st.error("Login is blocked until canonical Streamlit OIDC secrets are fixed.")
        for issue in errors:
            st.markdown(f"- {issue}")

    if callback_failed:
        st.warning(
            "Callback query parameters were received but no authenticated Streamlit session was created. "
            "Verify Auth0 callback URL is exactly https://exec-dash.streamlit.app/oauth2callback."
        )

    if configured_base and browser_base and configured_base != browser_base:
        st.warning(f"Configured redirect base ({configured_base}) does not match current browser base ({browser_base}).")

    if callback_attempts >= 2:
        st.info("Repeated callback attempts detected in this session. Clear local auth state and retry sign-in.")
        st.button("Reset sign-in state", on_click=clear_auth_session_state)

    if validation.warnings:
        for warning in validation.warnings:
            st.info(warning)

    st.button("Login with Auth0", on_click=login_with_auth0, type="primary", disabled=bool(errors))
    st.caption("Use your company account.")


def main() -> None:
    validation = validate_canonical_auth_config()
    if not validation.is_valid:
        _render_auth_config_error(validation)
        st.stop()

    if not safe_is_logged_in():
        sync_user_from_oidc()
        render_clean_login_screen(validation)
        st.stop()

    sync_user_from_oidc()
    streamlit_user = load_user_from_session()
    ctx = load_user_context(streamlit_user)

    with st.sidebar:
        st.caption(f"Signed in as {ctx.user.display_name or ctx.user.email or 'User'}")
        if st.button("Logout"):
            _logout()

    pages = build_pages(ctx)
    selected_page = st.navigation(pages, position="hidden")
    selected_page.run()


if __name__ == "__main__":
    try:
        configure_logging()
        configure_page()
        init_engine()
        main()
    except Exception as exc:  # pragma: no cover
        render_internal_error(exc, context="streamlit_app bootstrap/main execution")
