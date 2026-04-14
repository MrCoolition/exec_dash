from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Help / Definitions")
    st.markdown("""
- **Freshness**: fresh < 30 min, warning 30 min-4 hr, stale > 4 hr, critical stale > 24 hr.
- **Delivery health**: Green/Yellow/Red based on overdue pressure and critical blockers.
""")
