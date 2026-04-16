from __future__ import annotations

import streamlit as st

from app.ui.exec_components import section_bar
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state()
    st.title("Help & Support")
    section_bar("How reporting data flows")
    st.markdown(
        """
        - **Weekly Updates** captures the operational update for a specific program/week.
        - **Submit Update** publishes the latest executive snapshot to the Program and Portfolio views.
        - **Program One-Pager** shows the latest submitted update with fallback to current published snapshot.
        - **Impower Portfolio** rolls up the published program snapshot across your selected portfolio.
        """
    )
    section_bar("Need help?")
    st.write("Contact PMO support for data issues or your application admin for access problems.")
