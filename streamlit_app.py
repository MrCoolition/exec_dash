from __future__ import annotations

import streamlit as st

from app.core.auth import ensure_authenticated_user, load_user_context
from app.core.db import init_engine
from app.core.logging import configure_logging
from app.ui.layout import configure_page, render_shell
from app.ui.pages import build_pages


configure_logging()
configure_page()
init_engine()

streamlit_user = ensure_authenticated_user()
ctx = load_user_context(streamlit_user)

render_shell(ctx)
pages = build_pages(ctx)

pg = st.navigation(pages, position="top")
pg.run()
