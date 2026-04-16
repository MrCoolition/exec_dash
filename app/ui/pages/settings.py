from __future__ import annotations

import streamlit as st

from app.ui.exec_components import section_bar
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state()
    st.title("Settings")
    section_bar("Preferences")
    st.toggle("Email notifications", value=True)
    st.toggle("Show advanced portfolio indicators", value=True)
    st.selectbox("Default landing page", ["Impower Portfolio", "Program One-Pager", "Weekly Updates"])
    st.info("Settings are account-level preferences and will be persisted in a future release.")
