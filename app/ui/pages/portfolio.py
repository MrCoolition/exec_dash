from __future__ import annotations

import pandas as pd
import streamlit as st

from app.repositories.programs import list_program_snapshots_by_portfolio
from app.ui.pages.common import ensure_sidebar_state


def _status_color(status: str) -> str:
    return {"On Track": "🟢", "Needs Attention": "🟡", "At Risk": "🔴"}.get(status, "⚪")


def render() -> None:
    state = ensure_sidebar_state()
    portfolio = state.get("selected_portfolio")
    if not portfolio:
        st.warning("No portfolio data found for the selected program.")
        return

    programs = list_program_snapshots_by_portfolio(str(portfolio["id"]))
    st.title("Impower Portfolio")

    total = len(programs)
    at_risk = len([p for p in programs if p.get("current_status") == "At Risk"])
    needs_attention = len([p for p in programs if p.get("current_status") == "Needs Attention"])
    avg_complete = round(sum((p.get("percent_complete") or 0) for p in programs) / max(total, 1), 1)
    decisions_pending = len([p for p in programs if p.get("decision_needed")])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Programs", total)
    c2.metric("At Risk", at_risk)
    c3.metric("Delayed / Needs Attention", needs_attention)
    c4.metric("Average % Complete", f"{avg_complete}%")
    c5.metric("Decisions Pending", decisions_pending)

    st.subheader("Program Grid")
    for program in programs:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.markdown(f"### {_status_color(program.get('current_status'))} {program['name']}")
            left.caption(f"Phase: {program.get('current_phase')} · Complete: {program.get('percent_complete', 0)}%")
            left.write(program.get("summary") or "No summary")
            if right.button("Open", key=f"open-{program['id']}"):
                st.session_state.selected_program_id = str(program["id"])
                st.toast("Program selected. Open Program One-Pager from navigation.")

    st.subheader("Roadmap & Upcoming Milestones")
    roadmap_rows = [
        {
            "Program": p["name"],
            "Next Milestone": p.get("next_milestone_name"),
            "Date": p.get("next_milestone_date"),
            "Status": p.get("current_status"),
        }
        for p in programs
    ]
    st.dataframe(pd.DataFrame(roadmap_rows), hide_index=True, use_container_width=True)

    st.subheader("Key Risks Across Portfolio")
    risks = [{"Program": p["name"], "Risk": p.get("risk_detail"), "Mitigation": p.get("mitigation")} for p in programs if p.get("risk_detail")]
    st.dataframe(pd.DataFrame(risks or [{"Program": "-", "Risk": "No major risks logged", "Mitigation": "-"}]), hide_index=True, use_container_width=True)

    st.subheader("Executive Action Items / Decisions Needed")
    decisions = [
        {"Program": p["name"], "Decision Needed": p.get("decision_needed"), "Status Note": p.get("status_note")}
        for p in programs
        if p.get("decision_needed")
    ]
    st.dataframe(pd.DataFrame(decisions or [{"Program": "-", "Decision Needed": "None", "Status Note": "-"}]), hide_index=True, use_container_width=True)
