from __future__ import annotations

import streamlit as st

from app.ui.exec_reporting_views import render_html
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state(current_page="Settings")
    render_html("<div class='panel-header'><div class='eyebrow'>Administration</div><div class='heading'>Settings</div><div class='copy'>Configure your executive reporting preferences.</div></div>")
    c1, c2 = st.columns(2)
    with c1:
        render_html("<div class='card'><div class='heading'>Display</div><div class='copy'>Session-level options for parity release.</div></div>")
        st.selectbox("Default landing page", ["Impower Portfolio", "Program One-Pager", "Weekly Updates"], key="settings_landing")
        st.toggle("Show executive preview by default", value=True, key="settings_preview_default")
    with c2:
        render_html("<div class='card'><div class='heading'>Workflow</div><div class='copy'>Control weekly update authoring defaults.</div></div>")
        st.toggle("Enable autosave for lead updates", value=False, key="settings_autosave")
        st.selectbox("Default Portfolio", ["Current Sidebar Portfolio"], key="settings_default_portfolio")
