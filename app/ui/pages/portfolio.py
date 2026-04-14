from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Portfolio")
    st.segmented_control("Lens", ["Status", "Timeline"], key="portfolio_lens", default="Status")
    st.dataframe([
        {"program": "Program A", "status": "Green", "next_milestone": "2026-04-30"},
        {"program": "Program B", "status": "Yellow", "next_milestone": "2026-05-07"},
    ], use_container_width=True)
