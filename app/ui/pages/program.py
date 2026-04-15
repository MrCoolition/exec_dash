from __future__ import annotations

import pandas as pd
import streamlit as st

from app.repositories.programs import get_program
from app.repositories.weekly_updates import get_latest_submitted_update
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    state = ensure_sidebar_state()
    program_id = state["selected_program_id"]
    program = get_program(program_id)
    if not program:
        st.error("Selected program not found.")
        return

    latest = get_latest_submitted_update(program_id)

    st.title("Program One-Pager")
    st.subheader(program["name"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Overall Status", program.get("current_status") or "-")
    c2.metric("% Complete", f"{program.get('percent_complete') or 0}%")
    c3.metric("Current Phase", program.get("current_phase") or "-")

    st.markdown("### Executive Summary")
    st.write(program.get("summary") or "No summary available.")

    st.markdown("### Milestone Timeline")
    milestones = (latest or {}).get("milestones", [])
    milestone_df = pd.DataFrame(milestones or [{"milestone_name": "No milestone data", "planned_date": None, "forecast_date": None, "status": "-", "comment": "-"}])
    st.dataframe(milestone_df, hide_index=True, use_container_width=True)

    lcol, rcol = st.columns(2)
    with lcol:
        st.markdown("### Recent Accomplishments")
        st.write((latest or {}).get("accomplishments") or program.get("summary") or "No accomplishments logged.")

        st.markdown("### Upcoming Work")
        st.write((latest or {}).get("next_steps") or program.get("upcoming_work") or "No upcoming work logged.")

    with rcol:
        st.markdown("### Risks / Dependencies")
        risks = (latest or {}).get("risks", [])
        risk_df = pd.DataFrame(risks or [{"severity": "-", "risk_title": program.get("risk_detail") or "None", "mitigation": program.get("mitigation") or "-"}])
        st.dataframe(risk_df, hide_index=True, use_container_width=True)

        st.markdown("### Leadership Decisions")
        decisions = (latest or {}).get("decisions", [])
        decision_df = pd.DataFrame(decisions or [{"decision_topic": program.get("decision_needed") or "No pending decisions", "required_by": None, "impact_if_unresolved": "-", "recommendation": "-"}])
        st.dataframe(decision_df, hide_index=True, use_container_width=True)

    st.markdown("### Workstream Status")
    st.progress(min(max(int(program.get("percent_complete") or 0), 0), 100), text=f"{program.get('percent_complete') or 0}% Complete")
