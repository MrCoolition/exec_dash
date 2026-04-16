from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st

from app.repositories.programs import list_program_snapshots_by_portfolio
from app.services.view_models import build_portfolio_kpis, rank_program_risks
from app.ui.exec_components import empty_state, hero_block, section_bar
from app.ui.exec_formatters import format_date, has_text
from app.ui.pages.common import ensure_sidebar_state, open_program


def render() -> None:
    state = ensure_sidebar_state()
    portfolio = state.get("selected_portfolio")
    if not portfolio:
        empty_state("No portfolio data found for the selected program.")
        return

    programs = list_program_snapshots_by_portfolio(str(portfolio["id"]))
    week_ending = state["reporting_date"]

    hero_block(
        "Impower Portfolio",
        [
            ("Portfolio", portfolio.get("name", "Portfolio")),
            ("Week Ending", format_date(week_ending)),
            ("Refreshed", dt.datetime.utcnow().strftime("%H:%M UTC")),
            ("Programs", str(len(programs))),
        ],
    )

    kpi = build_portfolio_kpis(programs)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Programs", kpi["total"])
    c2.metric("At Risk", kpi["at_risk"])
    c3.metric("Delayed / Needs Attention", kpi["needs_attention"])
    c4.metric("Average % Complete", f"{kpi['avg_complete']}%")
    c5.metric("Decisions Pending", kpi["decisions_pending"])

    section_bar("Program Grid")
    for program in programs:
        with st.container(border=True):
            left, mid, right = st.columns([5, 3, 1])
            left.markdown(f"**{program['name']}**")
            left.caption(program.get("status_note") or program.get("summary") or "No status note")
            mid.caption(
                f"Status: {program.get('current_status') or 'Unknown'} | "
                f"Phase: {program.get('current_phase') or '—'} | "
                f"Complete: {program.get('percent_complete') or 0}%"
            )
            mid.caption(
                f"Owner: {program.get('owner_name') or '—'} | "
                f"Next Milestone: {program.get('next_milestone_name') or '—'} ({format_date(program.get('next_milestone_date'))})"
            )
            if right.button("Open", key=f"open-program-{program['id']}"):
                open_program(str(program["id"]))

    section_bar("Roadmap / Upcoming Milestones")
    roadmap_rows = [
        {
            "Program": p["name"],
            "Phase": p.get("current_phase") or "—",
            "Next Milestone": p.get("next_milestone_name") or "—",
            "Date": format_date(p.get("next_milestone_date")),
            "Status": p.get("current_status") or "Unknown",
        }
        for p in programs
    ]
    st.dataframe(pd.DataFrame(roadmap_rows), hide_index=True, use_container_width=True)

    section_bar("Key Risks Across Portfolio")
    risks = rank_program_risks(programs)
    if risks:
        st.dataframe(pd.DataFrame(risks), hide_index=True, use_container_width=True)
    else:
        empty_state("No key risks logged for this portfolio.")

    section_bar("Executive Action Items / Decisions Needed")
    decisions = [
        {"Program": p["name"], "Decision Needed": p.get("decision_needed"), "Status Note": p.get("status_note") or "—"}
        for p in programs
        if has_text(p.get("decision_needed"))
    ]
    if decisions:
        st.dataframe(pd.DataFrame(decisions), hide_index=True, use_container_width=True)
    else:
        empty_state("No leadership decisions are currently pending.")
