from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError

from app.core.auth import (
    APP_NAME,
    ensure_authenticated_user,
    load_user_context,
    login_with_auth0,
    render_auth_troubleshooting_panel,
    sync_user_from_oidc,
)
from app.core.db import init_engine
from app.core.logging import configure_logging
from app.core.error_reporting import render_internal_error
from app.ui.layout import configure_page, render_shell
from app.ui.pages import build_pages


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _safe_user_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except (StreamlitAuthError, StreamlitSecretNotFoundError) as exc:
        st.error(f"Authentication bootstrap failed: {exc}")
        return False


def _render_login_screen() -> None:
    st.title(APP_NAME)
    st.button("Login with Auth0", on_click=login_with_auth0)


def _oauth_callback_error_detail() -> str | None:
    query_params = st.query_params
    code = query_params.get("code")
    state = query_params.get("state")
    oauth_error = query_params.get("error")
    oauth_error_description = query_params.get("error_description")

    if oauth_error:
        if oauth_error_description:
            return f"{oauth_error}: {oauth_error_description}"
        return str(oauth_error)
    if code and state:
        return "Received OAuth callback parameters, but no authenticated session was established."
    return None


def main() -> None:
    if not _safe_user_logged_in():
        callback_error_detail = _oauth_callback_error_detail()
        if callback_error_detail:
            st.error(
                "Login returned from Auth0, but the app could not complete sign in. "
                "Check auth configuration and try again."
            )
            render_auth_troubleshooting_panel(callback_error_detail)
        _render_login_screen()
        st.stop()

    sync_user_from_oidc()

    if st.session_state.get("authenticated", False):
        with st.sidebar:
            st.write(f"🔌 Logged in as: {st.session_state['username']}")
            if st.button("Logout"):
                st.logout()
                st.rerun()

        streamlit_user = ensure_authenticated_user()
        ctx = load_user_context(streamlit_user)
        render_shell(ctx)
        pages = build_pages(ctx)
        pg = st.navigation(pages, position="top")
        pg.run()
    else:
        _render_login_screen()


if __name__ == "__main__":
    try:
        configure_logging()
        configure_page()
        init_engine()
        main()
    except Exception as exc:  # pragma: no cover - visual runtime fallback
        render_internal_error(exc, context="streamlit_app bootstrap/main execution")
