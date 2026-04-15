from __future__ import annotations

import streamlit as st

from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state()
    st.title("Help & Support")
    st.markdown(
        """
        ### Need assistance?

        - Contact the PMO support desk for portfolio data issues.
        - Use Weekly Updates to save draft progress and submit published snapshots.
        - Dashboard and Program One-Pager show only submitted, published data.
        """
    )
