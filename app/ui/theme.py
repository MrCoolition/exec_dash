from __future__ import annotations

import streamlit as st


def inject_theme_overrides() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.2rem;}
        div[data-testid="stMetric"] {border: 1px solid #e9edf5; border-radius: 12px; padding: 0.6rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )
