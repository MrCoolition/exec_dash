from __future__ import annotations

import datetime as dt

import streamlit as st

from app.repositories.portfolios import get_portfolio_by_program
from app.repositories.programs import list_programs


PROGRAM_PAGE_PATH = "app/ui/pages/program.py"


def open_program(program_id: str) -> None:
    st.session_state.selected_program_id = program_id
    try:
        st.switch_page(PROGRAM_PAGE_PATH)
    except Exception:
        pass


def ensure_sidebar_state() -> dict:
    programs = list_programs()
    if not programs:
        return {"programs": [], "selected_program": None, "selected_program_id": None, "reporting_date": dt.date.today()}

    if "selected_program_id" not in st.session_state:
        st.session_state.selected_program_id = str(programs[0]["id"])
    if "reporting_date" not in st.session_state:
        st.session_state.reporting_date = dt.date.today()

    with st.sidebar:
        st.markdown("#### Reporting Context")
        selected_id = st.selectbox(
            "Program",
            options=[str(p["id"]) for p in programs],
            format_func=lambda pid: next((p["name"] for p in programs if str(p["id"]) == pid), pid),
            key="selected_program_id",
        )
        st.date_input("Reporting Week Ending", key="reporting_date")

    selected_program = next((p for p in programs if str(p["id"]) == str(selected_id)), programs[0])
    portfolio = get_portfolio_by_program(str(selected_program["id"]))

    with st.sidebar:
        st.caption(f"Portfolio: {(portfolio or {}).get('name', 'Unknown')}")
        st.caption(f"Program: {selected_program['name']}")

    return {
        "programs": programs,
        "selected_program": selected_program,
        "selected_program_id": str(selected_program["id"]),
        "selected_portfolio": portfolio,
        "reporting_date": st.session_state.reporting_date,
    }
