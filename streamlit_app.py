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
    initial_sidebar_state="expanded",
)

NAV_POSITION = "sidebar"


def _safe_user_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except (StreamlitAuthError, StreamlitSecretNotFoundError) as exc:
        st.error("Authentication is not available yet. Check app secrets and try again.")
        st.caption(f"Details: {exc}")
        return False


def _render_login_screen() -> None:
    st.title(APP_NAME)
    st.write("Sign in to access the Impower Portfolio Command Center.")
    st.button("Login with Auth0", on_click=login_with_auth0, type="primary")
    with st.expander("Authentication troubleshooting", expanded=False):
        render_auth_troubleshooting_panel()


def main() -> None:
    if not _safe_user_logged_in():
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
        pg = st.navigation(pages, position=NAV_POSITION)
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
