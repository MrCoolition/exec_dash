from __future__ import annotations

import streamlit as st

from app.core.permissions import can_access_admin, can_edit_updates
from app.services.user_context import UserContext
from app.ui.pages import ado, admin, diagnostics, help, portfolio, program, settings, update_center


def build_pages(ctx: UserContext) -> list[st.Page]:
    pages = [
        st.Page(portfolio.render, title="Impower Portfolio", icon=":material/grid_view:", url_path="portfolio"),
        st.Page(program.render, title="Program One-Pager", icon=":material/description:", url_path="program"),
        st.Page(
            lambda: update_center.render(ctx),
            title="Weekly Updates",
            icon=":material/edit:",
            url_path="updates",
            visibility="default" if can_edit_updates(ctx) else "hidden",
        ),
        st.Page(ado.render, title="ADO", icon=":material/sync:", url_path="ado"),
        st.Page(settings.render, title="Settings", icon=":material/settings:", url_path="settings"),
        st.Page(help.render, title="Help & Support", icon=":material/help:", url_path="help"),
    ]
    if can_access_admin(ctx):
        pages.extend([
            st.Page(
                lambda: admin.render(ctx),
                title="Admin",
                icon=":material/admin_panel_settings:",
                url_path="admin",
                visibility="hidden",
            ),
            st.Page(
                lambda: diagnostics.render(ctx),
                title="Diagnostics",
                icon=":material/monitoring:",
                url_path="diagnostics",
                visibility="hidden",
            ),
        ])
    return pages
