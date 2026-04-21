from __future__ import annotations

import datetime as dt
from html import escape

import pandas as pd
import streamlit as st

from app.repositories.programs import get_program
from app.repositories.weekly_updates import (
    PHASE_OPTIONS,
    RISK_SEVERITY_OPTIONS,
    STATUS_OPTIONS,
    TREND_OPTIONS,
    get_latest_submitted_update,
    get_weekly_update,
    list_decisions,
    list_milestones,
    list_risks,
    resolve_app_user_id,
    reset_weekly_update,
    save_weekly_update_draft,
    submit_weekly_update,
)
from app.services.user_context import UserContext
from app.ui.exec_components import dashboard_status_tag, render_html, render_html_table, section_bar
from app.ui.exec_formatters import has_text
from app.ui.pages.common import ensure_sidebar_state


def _seed_defaults(program_id: str, week_ending: dt.date) -> dict:
    existing = get_weekly_update(program_id, week_ending)
    if existing:
        return {**existing, "milestones": list_milestones(existing["id"]), "risks": list_risks(existing["id"]), "decisions": list_decisions(existing["id"])}

    latest = get_latest_submitted_update(program_id) or {}
    program = get_program(program_id) or {}
    return {
        "program_id": program_id,
        "week_ending": week_ending,
        "overall_status": latest.get("overall_status") or program.get("current_status") or "On Track",
        "current_phase": latest.get("current_phase") or program.get("current_phase") or "Discovery",
        "percent_complete": int(latest.get("percent_complete") or program.get("percent_complete") or 0),
        "trend": latest.get("trend") or "Flat",
        "accomplishments": latest.get("accomplishments") or "",
        "dependencies": latest.get("dependencies") or "",
        "next_steps": latest.get("next_steps") or program.get("upcoming_work") or "",
        "executive_summary": latest.get("executive_summary") or program.get("summary") or "",
        "milestones": latest.get("milestones") or [],
        "risks": latest.get("risks") or [],
        "decisions": latest.get("decisions") or [],
    }


def _load_into_state(seed: dict) -> None:
    st.session_state.wu_week_ending = seed.get("week_ending")
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


def _submitted_by(ctx: UserContext) -> str | None:
    return resolve_app_user_id(ctx.user.provider_sub, ctx.user.email)


def _payload(program_id: str, submitted_by: str | None) -> dict:
    return {
        "program_id": program_id,
        "week_ending": st.session_state.get("wu_week_ending"),
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


def _readiness(payload: dict) -> list[str]:
    issues = []
    if not has_text(payload.get("executive_summary")):
        issues.append("Executive Summary Notes")
    if not has_text(payload.get("accomplishments")):
        issues.append("Key Accomplishments This Week")
    if len(payload.get("milestones", [])) == 0:
        issues.append("At least one milestone")
    return issues


def render(ctx: UserContext) -> None:
    state = ensure_sidebar_state(current_page="Weekly Updates")
    program_id = state["selected_program_id"]
    program = get_program(program_id) or {}
    week_ending = state["reporting_date"]

    state_key = f"wu::{program_id}::{week_ending.isoformat()}"
    if st.session_state.get("wu_loaded_key") != state_key:
        _load_into_state(_seed_defaults(program_id, week_ending))
        st.session_state.wu_loaded_key = state_key

    render_html(
        "<div class='weekly-hero'>"
        f"<div class='weekly-hero-title'>Weekly Updates — {escape(program.get('name') or 'Program')}</div>"
        f"<div class='weekly-hero-sub'>{escape(program.get('portfolio_name') or 'Portfolio')} • Sponsor {escape(program.get('sponsor_name') or '—')} • Lead {escape(program.get('owner_name') or '—')}</div>"
        f"<div class='weekly-hero-metrics'>{dashboard_status_tag(st.session_state.get('wu_overall_status'))} <span class='update-pill'>{st.session_state.get('wu_percent_complete', 0)}%</span> <span class='update-pill'>{escape(st.session_state.get('wu_current_phase') or '—')}</span></div>"
        "<div class='weekly-section-copy'>Submitted data updates portfolio and one-pager automatically.</div>"
        "</div>"
    )

    section_bar("Core Status Inputs", "Enter this reporting week's executive status.")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.date_input("Week Ending Date", key="wu_week_ending")
    c2.selectbox("Overall Status", sorted(STATUS_OPTIONS), key="wu_overall_status")
    c3.selectbox("Current Phase", sorted(PHASE_OPTIONS), key="wu_current_phase")
    c4.slider("% Complete", 0, 100, key="wu_percent_complete")
    c5.selectbox("Trend", sorted(TREND_OPTIONS), key="wu_trend")

    section_bar("Milestone Updates")
    st.session_state.wu_milestones = st.data_editor(
        pd.DataFrame(st.session_state.get("wu_milestones", [])),
        key="wu_milestones_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "milestone_name": "Milestone Name",
            "planned_date": st.column_config.DateColumn("Planned Date"),
            "forecast_date": st.column_config.DateColumn("Forecast Date"),
            "status": st.column_config.SelectboxColumn("Status", options=sorted(STATUS_OPTIONS)),
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
        key="wu_risks_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "severity": st.column_config.SelectboxColumn("Severity", options=sorted(RISK_SEVERITY_OPTIONS)),
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
        key="wu_decisions_editor",
        num_rows="dynamic",
        width="stretch",
        column_config={
            "decision_topic": "Decision Topic",
            "required_by": st.column_config.DateColumn("Required By"),
            "impact_if_unresolved": "Impact if Unresolved",
            "recommendation": "Recommendation",
        },
    ).to_dict("records")

    payload = _payload(program_id, _submitted_by(ctx))

    section_bar("Executive Preview")
    st.markdown(f"{dashboard_status_tag(payload.get('overall_status'))} {payload.get('percent_complete', 0)}% complete, trend {payload.get('trend')}, week ending {payload.get('week_ending')}", unsafe_allow_html=True)
    st.write(payload.get("executive_summary") or "No executive summary yet.")
    render_html_table(pd.DataFrame(payload.get("decisions", [])), ["decision_topic", "required_by", "impact_if_unresolved"])
    render_html_table(pd.DataFrame(payload.get("risks", [])).head(3), ["severity", "risk_title", "owner_name", "target_date"])

    section_bar("Submission Readiness")
    issues = _readiness(payload)
    if issues:
        st.warning(f"{len(issues)} required item(s) missing.")
        for item in issues:
            st.caption(f"• {item}")
    else:
        st.success("Ready to submit.")

    b1, b2, b3 = st.columns(3)
    if b1.button("Save Draft"):
        try:
            save_weekly_update_draft(payload)
            st.success("Draft saved.")
        except ValueError as ex:
            st.error(str(ex))

    if b2.button("Submit Update", type="primary"):
        try:
            submit_weekly_update(payload)
            st.success("Weekly update submitted and published.")
        except ValueError as ex:
            st.error(str(ex))

    if b3.button("Reset Program"):
        seed = reset_weekly_update(program_id, week_ending) or _seed_defaults(program_id, week_ending)
        _load_into_state(seed)
        st.success("Form reset.")
        st.rerun()
