from __future__ import annotations

import streamlit as st


def freshness_badge(status: str, last_sync: str) -> None:
    st.caption(f"Sync: {status} · Last successful: {last_sync}")
