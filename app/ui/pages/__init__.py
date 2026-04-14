from __future__ import annotations

import streamlit as st

from app.core.permissions import can_access_admin, can_edit_updates
from app.services.user_context import UserContext
from app.ui.pages import admin, diagnostics, help, overview, portfolio, program, releases, team, update_center


def build_pages(ctx: UserContext) -> list[st.Page]:
    pages = [
        st.Page(overview.render, title="Overview", icon=":material/dashboard:"),
        st.Page(portfolio.render, title="Portfolio", icon=":material/grid_view:"),
        st.Page(program.render, title="Program", icon=":material/description:"),
        st.Page(team.render, title="Team", icon=":material/groups:"),
        st.Page(releases.render, title="Releases", icon=":material/rocket_launch:"),
        st.Page(help.render, title="Help", icon=":material/help:"),
    ]
    if can_edit_updates(ctx):
        pages.append(st.Page(lambda: update_center.render(ctx), title="Update Center", icon=":material/edit:", visibility="hidden"))
    if can_access_admin(ctx):
        pages.extend([
            st.Page(lambda: admin.render(ctx), title="Admin", icon=":material/admin_panel_settings:", visibility="hidden"),
            st.Page(lambda: diagnostics.render(ctx), title="Diagnostics", icon=":material/monitoring:", visibility="hidden"),
        ])
    return pages
