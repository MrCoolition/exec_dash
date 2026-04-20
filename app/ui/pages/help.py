from __future__ import annotations

import streamlit as st

from app.ui.exec_components import section_bar
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state()
    st.title("Help & Support")
    section_bar("Executive reporting guidance")
    st.markdown(
        """
        - Use **Weekly Updates** to enter current week status, milestones, risks, and decision requests.
        - Use **Program One-Pager** to review the leadership version of a single program.
        - Use **Impower Portfolio** for portfolio-wide oversight of milestones, risks, and action items.
        """
    )
    section_bar("Support")
    st.write("For access or data support, contact PMO Support through the standard product support channel.")
