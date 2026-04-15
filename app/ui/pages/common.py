from __future__ import annotations

import datetime as dt

import streamlit as st

from app.repositories.portfolios import get_portfolio_by_program
from app.repositories.programs import list_programs


def ensure_sidebar_state() -> dict:
    programs = list_programs()
    if not programs:
        return {"programs": [], "selected_program": None, "selected_program_id": None, "reporting_date": dt.date.today()}

    if "selected_program_id" not in st.session_state:
        st.session_state.selected_program_id = str(programs[0]["id"])
    if "reporting_date" not in st.session_state:
        st.session_state.reporting_date = dt.date.today()

    selected_id = st.sidebar.selectbox(
        "Program",
        options=[str(p["id"]) for p in programs],
        format_func=lambda pid: next((p["name"] for p in programs if str(p["id"]) == pid), pid),
        key="selected_program_id",
    )

    st.sidebar.date_input("Reporting Date", key="reporting_date")
    selected_program = next((p for p in programs if str(p["id"]) == str(selected_id)), programs[0])
    portfolio = get_portfolio_by_program(str(selected_program["id"]))
    st.sidebar.caption(f"Portfolio: {(portfolio or {}).get('name', 'Unknown')}")
    st.sidebar.caption(f"Program: {selected_program['name']}")

    return {
        "programs": programs,
        "selected_program": selected_program,
        "selected_program_id": str(selected_program["id"]),
        "selected_portfolio": portfolio,
        "reporting_date": st.session_state.reporting_date,
    }
