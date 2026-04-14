from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Program Detail")
    st.subheader("Program One-Pager")
    t1, t2, t3 = st.tabs(["Summary", "Risks", "Decisions"])
    with t1:
        st.write("Executive summary and current health.")
    with t2:
        st.dataframe([{"risk": "Vendor dependency", "severity": "High"}], use_container_width=True)
    with t3:
        st.dataframe([{"decision": "Scope approval", "due": "2026-04-18"}], use_container_width=True)
