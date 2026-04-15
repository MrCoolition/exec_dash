from __future__ import annotations

import streamlit as st

from app.core.permissions import can_access_admin
from app.services.user_context import UserContext
from app.ui.pages import admin, diagnostics, help, portfolio, program, settings, update_center


def build_pages(ctx: UserContext) -> list[st.Page]:
    pages = [
        st.Page(portfolio.render, title="Impower Portfolio", icon=":material/grid_view:"),
        st.Page(program.render, title="Program One-Pager", icon=":material/description:"),
        st.Page(lambda: update_center.render(ctx), title="Weekly Updates", icon=":material/edit:"),
        st.Page(settings.render, title="Settings", icon=":material/settings:"),
        st.Page(help.render, title="Help & Support", icon=":material/help:"),
    ]
    if can_access_admin(ctx):
        pages.extend([
            st.Page(lambda: admin.render(ctx), title="Admin", icon=":material/admin_panel_settings:", visibility="hidden"),
            st.Page(lambda: diagnostics.render(ctx), title="Diagnostics", icon=":material/monitoring:", visibility="hidden"),
        ])
    return pages
