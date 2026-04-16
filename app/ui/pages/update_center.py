from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st

from app.repositories.programs import get_program
from app.repositories.portfolios import get_portfolio
from app.repositories.weekly_updates import (
    get_latest_submitted_update,
    get_weekly_update,
    list_decisions,
    list_milestones,
    list_risks,
    reset_weekly_update,
    save_weekly_update_draft,
    submit_weekly_update,
)
from app.services.user_context import UserContext
from app.ui.exec_components import hero_block, section_bar
from app.ui.exec_formatters import has_text
from app.ui.pages.common import ensure_sidebar_state


STATUS_OPTIONS = ["On Track", "Needs Attention", "At Risk"]
PHASE_OPTIONS = ["Discovery", "Phase 1", "Phase 2", "Phase 3", "Phase 4"]
TREND_OPTIONS = ["Up", "Flat", "Down"]
RISK_SEVERITY_OPTIONS = ["High", "Medium", "Low", "DEP"]


def _seed_defaults(program_id: str, week_ending: dt.date) -> dict:
    existing = get_weekly_update(program_id, week_ending)
    if existing:
        return {
            **existing,
            "milestones": list_milestones(existing["id"]),
            "risks": list_risks(existing["id"]),
            "decisions": list_decisions(existing["id"]),
        }

    program = get_program(program_id) or {}
    latest = get_latest_submitted_update(program_id) or {}
    return {
        "program_id": program_id,
        "week_ending": week_ending,
        "overall_status": latest.get("overall_status") or program.get("current_status") or "On Track",
        "current_phase": latest.get("current_phase") or program.get("current_phase") or "Discovery",
        "percent_complete": int(latest.get("percent_complete") or program.get("percent_complete") or 0),
        "trend": latest.get("trend") or "Flat",
        "accomplishments": latest.get("accomplishments") or "",
        "dependencies": latest.get("dependencies") or program.get("risk_detail") or "",
        "next_steps": latest.get("next_steps") or program.get("upcoming_work") or "",
        "executive_summary": latest.get("executive_summary") or program.get("summary") or "",
        "milestones": latest.get("milestones") or [],
        "risks": latest.get("risks") or [],
        "decisions": latest.get("decisions") or [],
    }


def _load_into_state(seed: dict) -> None:
    st.session_state.wu_overall_status = seed.get("overall_status", "On Track")
    st.session_state.wu_current_phase = seed.get("current_phase", "Discovery")
    st.session_state.wu_percent_complete = int(seed.get("percent_complete") or 0)
    st.session_state.wu_trend = seed.get("trend", "Flat")
    st.session_state.wu_accomplishments = seed.get("accomplishments", "")
    st.session_state.wu_dependencies = seed.get("dependencies", "")
    st.session_state.wu_next_steps = seed.get("next_steps", "")
    st.session_state.wu_executive_summary = seed.get("executive_summary", "")
    st.session_state.wu_milestones = seed.get("milestones", [])
    st.session_state.wu_risks = seed.get("risks", [])
    st.session_state.wu_decisions = seed.get("decisions", [])


def _payload(program_id: str, week_ending: dt.date, submitted_by: str | None) -> dict:
    return {
        "program_id": program_id,
        "week_ending": week_ending,
        "overall_status": st.session_state.get("wu_overall_status"),
        "current_phase": st.session_state.get("wu_current_phase"),
        "percent_complete": int(st.session_state.get("wu_percent_complete", 0)),
        "trend": st.session_state.get("wu_trend"),
        "accomplishments": st.session_state.get("wu_accomplishments", ""),
        "dependencies": st.session_state.get("wu_dependencies", ""),
        "next_steps": st.session_state.get("wu_next_steps", ""),
        "executive_summary": st.session_state.get("wu_executive_summary", ""),
        "milestones": st.session_state.get("wu_milestones", []),
        "risks": st.session_state.get("wu_risks", []),
        "decisions": st.session_state.get("wu_decisions", []),
        "submitted_by": submitted_by,
    }


def _submitted_by(ctx: UserContext) -> str | None:
    return ctx.user.email or ctx.user.provider_sub


def _readiness(payload: dict) -> tuple[bool, list[str]]:
    checks = [
        (has_text(payload.get("executive_summary")), "Executive summary is required."),
        (len(payload.get("milestones", [])) > 0, "At least one milestone is required."),
        (has_text(payload.get("accomplishments")), "Accomplishments are required."),
    ]
    issues = [msg for ok, msg in checks if not ok]
    return (len(issues) == 0, issues)


def render(ctx: UserContext) -> None:
    state = ensure_sidebar_state()
    program_id = state["selected_program_id"]
    week_ending = state["reporting_date"]
    state_key = f"wu_loaded::{program_id}::{week_ending.isoformat()}"

    program = get_program(program_id) or {}
    portfolio = get_portfolio(program.get("portfolio_id")) or {}

    if st.session_state.get("wu_loaded_key") != state_key:
        _load_into_state(_seed_defaults(program_id, week_ending))
        st.session_state.wu_loaded_key = state_key

    hero_block(
        "Weekly Updates",
        [
            ("Program", program.get("name") or "—"),
            ("Portfolio", portfolio.get("name") or "—"),
            ("Sponsor", program.get("sponsor_name") or "—"),
            ("Lead", program.get("owner_name") or "—"),
            ("Week Ending", week_ending.isoformat()),
            ("Status", st.session_state.get("wu_overall_status") or "Unknown"),
            ("Phase", st.session_state.get("wu_current_phase") or "—"),
            ("% Complete", f"{st.session_state.get('wu_percent_complete', 0)}%"),
        ],
    )

    section_bar("Status Entry")
    c1, c2, c3, c4 = st.columns(4)
    c1.selectbox("Overall Status", STATUS_OPTIONS, key="wu_overall_status")
    c2.selectbox("Current Phase", PHASE_OPTIONS, key="wu_current_phase")
    c3.slider("Percent Complete", 0, 100, key="wu_percent_complete")
    c4.selectbox("Trend vs Prior Week", TREND_OPTIONS, key="wu_trend")

    section_bar("Milestones")
    st.session_state.wu_milestones = st.data_editor(
        pd.DataFrame(st.session_state.get("wu_milestones", [])),
        num_rows="dynamic",
        use_container_width=True,
        key="wu_milestones_editor",
        column_config={
            "milestone_name": "Milestone Name",
            "planned_date": st.column_config.DateColumn("Planned Date"),
            "forecast_date": st.column_config.DateColumn("Forecast Date"),
            "status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
            "comment": "Comment",
        },
    ).to_dict("records")

    section_bar("Narrative")
    st.text_area("Key Accomplishments This Week", key="wu_accomplishments")
    st.text_area("Dependencies & Blockers", key="wu_dependencies")
    st.text_area("Planned Next Steps", key="wu_next_steps")
    st.text_area("Executive Summary Notes", key="wu_executive_summary")

    section_bar("Risks & Mitigations")
    st.session_state.wu_risks = st.data_editor(
        pd.DataFrame(st.session_state.get("wu_risks", [])),
        num_rows="dynamic",
        use_container_width=True,
        key="wu_risks_editor",
        column_config={
            "severity": st.column_config.SelectboxColumn("Severity", options=RISK_SEVERITY_OPTIONS),
            "risk_title": "Risk Title",
            "owner_name": "Owner",
            "target_date": st.column_config.DateColumn("Target Date"),
            "description": "Description",
            "mitigation": "Mitigation",
        },
    ).to_dict("records")

    section_bar("Leadership Decision Requests")
    st.session_state.wu_decisions = st.data_editor(
        pd.DataFrame(st.session_state.get("wu_decisions", [])),
        num_rows="dynamic",
        use_container_width=True,
        key="wu_decisions_editor",
        column_config={
            "decision_topic": "Decision Topic",
            "required_by": st.column_config.DateColumn("Required By"),
            "impact_if_unresolved": "Impact if Unresolved",
            "recommendation": "Recommendation",
        },
    ).to_dict("records")

    submitted_by = _submitted_by(ctx)
    payload = _payload(program_id, week_ending, submitted_by)

    section_bar("Executive Preview")
    st.write(payload["executive_summary"] or "No executive summary yet.")
    st.dataframe(pd.DataFrame(payload["milestones"]), use_container_width=True, hide_index=True)

    section_bar("Submission Readiness")
    ready, issues = _readiness(payload)
    if ready:
        st.success("Ready to submit.")
    else:
        st.warning("Not ready to submit yet.")
        for issue in issues:
            st.caption(f"• {issue}")

    b1, b2, b3 = st.columns(3)
    if b1.button("Save Draft"):
        try:
            save_weekly_update_draft(payload)
            st.success("Draft saved.")
        except Exception:
            st.error("Failed to save draft.")

    if b2.button("Submit Update", type="primary"):
        try:
            submit_weekly_update(payload)
            st.success("Weekly update submitted and published.")
        except Exception:
            st.error("Submit failed.")

    if b3.button("Reset Program"):
        reset_data = reset_weekly_update(program_id, week_ending) or _seed_defaults(program_id, week_ending)
        _load_into_state(reset_data)
        st.success("Form reset.")
        st.rerun()
