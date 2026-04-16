from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError

from app.core.auth import APP_NAME, ensure_authenticated_user, load_user_context, login_with_auth0, sync_user_from_oidc
from app.core.db import init_engine
from app.core.error_reporting import render_internal_error
from app.core.logging import configure_logging
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
    except (StreamlitAuthError, StreamlitSecretNotFoundError):
        st.error("Unable to start sign in right now. Please try again shortly.")
        return False


def render_clean_login_screen() -> None:
    st.title(APP_NAME)
    st.caption("Executive reporting command center")
    st.button("Login with Auth0", on_click=login_with_auth0, type="primary")
    st.caption("Use your company account.")


def main() -> None:
    if not _safe_user_logged_in():
        render_clean_login_screen()
        st.stop()

    sync_user_from_oidc()
    streamlit_user = ensure_authenticated_user()
    ctx = load_user_context(streamlit_user)

    with st.sidebar:
        st.caption(f"Signed in as {ctx.user.display_name or ctx.user.email or 'User'}")
        if st.button("Logout"):
            st.logout()

    render_shell(ctx)
    pages = build_pages(ctx)
    pg = st.navigation(pages, position="top")
    pg.run()


if __name__ == "__main__":
    try:
        configure_logging()
        configure_page()
        init_engine()
        main()
    except Exception as exc:  # pragma: no cover - visual runtime fallback
        render_internal_error(exc, context="streamlit_app bootstrap/main execution")
