from __future__ import annotations

import streamlit as st

from app.ui.exec_components import section_bar
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state()
    st.title("Settings")
    section_bar("Executive Preferences")
    st.selectbox("Default Portfolio", ["Current Sidebar Portfolio"], key="settings_default_portfolio")
    st.toggle("Enable autosave for lead updates", value=False, key="settings_autosave")
    st.selectbox("Default landing page", ["Impower Portfolio", "Program One-Pager", "Weekly Updates"], key="settings_landing")
    st.toggle("Show executive preview by default", value=True, key="settings_preview_default")
    st.caption("Settings are saved in session for this parity release.")
