from __future__ import annotations

import pandas as pd
import streamlit as st

from app.repositories.programs import get_program
from app.repositories.portfolios import get_portfolio
from app.repositories.weekly_updates import get_latest_submitted_update
from app.services.view_models import build_signal_cards, sort_milestones
from app.ui.exec_components import empty_state, hero_block, section_bar
from app.ui.exec_formatters import has_text
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    state = ensure_sidebar_state()
    program_id = state["selected_program_id"]
    program = get_program(program_id)
    if not program:
        st.error("Selected program not found.")
        return

    portfolio = get_portfolio(program.get("portfolio_id")) or {}
    latest = get_latest_submitted_update(program_id)

    hero_block(
        program["name"],
        [
            ("Portfolio", portfolio.get("name") or "—"),
            ("Executive Sponsor", program.get("sponsor_name") or "—"),
            ("Program Lead", program.get("owner_name") or "—"),
            ("Status", program.get("current_status") or "Unknown"),
            ("% Complete", f"{program.get('percent_complete') or 0}%"),
            ("Current Phase", program.get("current_phase") or "—"),
        ],
    )

    section_bar("Executive Summary")
    st.write((latest or {}).get("executive_summary") or program.get("summary") or "No summary available.")

    section_bar("Milestone Timeline")
    milestones = sort_milestones((latest or {}).get("milestones", []))
    if milestones:
        st.dataframe(pd.DataFrame(milestones), hide_index=True, use_container_width=True)
    else:
        empty_state("No submitted milestones available.")

    lcol, rcol = st.columns(2)
    with lcol:
        section_bar("Recent Accomplishments")
        st.write((latest or {}).get("accomplishments") or program.get("summary") or "No accomplishments logged.")

        section_bar("Upcoming Work")
        st.write((latest or {}).get("next_steps") or program.get("upcoming_work") or "No upcoming work logged.")

    with rcol:
        section_bar("Risks / Issues / Dependencies")
        risks = (latest or {}).get("risks", [])
        if risks:
            st.dataframe(pd.DataFrame(risks), hide_index=True, use_container_width=True)
        elif has_text(program.get("risk_detail")):
            st.dataframe(pd.DataFrame([{"risk_title": program.get("risk_detail"), "mitigation": program.get("mitigation") or "—"}]), hide_index=True, use_container_width=True)
        else:
            empty_state("No material risks logged.")

        section_bar("Leadership Decisions Needed")
        decisions = (latest or {}).get("decisions", [])
        if decisions:
            st.dataframe(pd.DataFrame(decisions), hide_index=True, use_container_width=True)
        elif has_text(program.get("decision_needed")):
            st.dataframe(pd.DataFrame([{"decision_topic": program.get("decision_needed")}]), hide_index=True, use_container_width=True)
        else:
            empty_state("No leadership decisions pending.")

    section_bar("Execution Signals")
    cards = build_signal_cards(program, latest)
    cols = st.columns(len(cards))
    for col, (title, value) in zip(cols, cards):
        col.metric(title, value)
