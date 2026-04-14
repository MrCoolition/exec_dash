from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Team / Sprint Delivery")
    c1, c2, c3 = st.columns(3)
    c1.metric("Committed", 24)
    c2.metric("Completed", 19)
    c3.metric("Carryover", 5)
