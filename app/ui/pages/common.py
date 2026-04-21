from __future__ import annotations

import datetime as dt

import streamlit as st

from app.repositories.portfolios import get_portfolio_by_program
from app.repositories.programs import list_programs

PROGRAM_PAGE_PATH = "app/ui/pages/program.py"
PORTFOLIO_PAGE_PATH = "app/ui/pages/portfolio.py"
UPDATES_PAGE_PATH = "app/ui/pages/update_center.py"
SETTINGS_PAGE_PATH = "app/ui/pages/settings.py"
HELP_PAGE_PATH = "app/ui/pages/help.py"


def open_program(program_id: str) -> None:
    st.session_state.selected_program_id = program_id
    try:
        st.switch_page(PROGRAM_PAGE_PATH)
    except Exception:
        pass


def _nav_button(label: str, path: str, current_page: str) -> None:
    is_active = label == current_page
    if st.button(label, use_container_width=True, type="primary" if is_active else "secondary") and not is_active:
        try:
            st.switch_page(path)
        except Exception:
            pass


def ensure_sidebar_state(current_page: str = "Impower Portfolio") -> dict:
    programs = list_programs()
    if not programs:
        return {"programs": [], "selected_program": None, "selected_program_id": None, "reporting_date": dt.date.today()}

    if "selected_program_id" not in st.session_state:
        st.session_state.selected_program_id = str(programs[0]["id"])
    if "reporting_date" not in st.session_state:
        st.session_state.reporting_date = dt.date.today()

    with st.sidebar:
        st.markdown("### Program Context")
        selected_id = st.selectbox(
            "Program",
            options=[str(p["id"]) for p in programs],
            format_func=lambda pid: next((p["name"] for p in programs if str(p["id"]) == pid), pid),
            key="selected_program_id",
        )
        st.date_input("Reporting Date", key="reporting_date", format="YYYY/MM/DD")

    selected_program = next((p for p in programs if str(p["id"]) == str(selected_id)), programs[0])
    portfolio = get_portfolio_by_program(str(selected_program["id"]))

    with st.sidebar:
        st.markdown("#### Navigation")
        _nav_button("Impower Portfolio", PORTFOLIO_PAGE_PATH, current_page)
        _nav_button("Program One-Pager", PROGRAM_PAGE_PATH, current_page)
        _nav_button("Weekly Updates", UPDATES_PAGE_PATH, current_page)
        _nav_button("Settings", SETTINGS_PAGE_PATH, current_page)
        _nav_button("Help & Support", HELP_PAGE_PATH, current_page)
        st.markdown("### Context")
        st.caption(
            f"Selected portfolio: {(portfolio or {}).get('name', 'Unknown')}. "
            "Program leads update weekly status and leadership consumes program-relevant views."
        )

    return {
        "programs": programs,
        "selected_program": selected_program,
        "selected_program_id": str(selected_program["id"]),
        "selected_portfolio": portfolio,
        "reporting_date": st.session_state.reporting_date,
        "current_user": st.session_state.get("user"),
    }
