from __future__ import annotations

import streamlit as st

from app.services.user_context import UserContext
from app.ui.theme import inject_theme_overrides
from app.ui.widgets import freshness_badge


def configure_page() -> None:
    inject_theme_overrides()


def render_shell(ctx: UserContext) -> None:
    cols = st.columns([4, 3, 2])
    with cols[0]:
        st.markdown("### Executive Reporting Dashboard")
    with cols[1]:
        st.caption(f"User: {ctx.user.display_name or ctx.user.email or 'User'}")
        st.caption(f"Roles: {', '.join(sorted(ctx.role_codes))}")
    with cols[2]:
        freshness_badge("Refreshed", "just now")
