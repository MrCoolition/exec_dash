from __future__ import annotations

from datetime import date
from html import escape

import pandas as pd
import streamlit as st

from app.repositories.programs import get_program
from app.repositories.weekly_updates import get_latest_submitted_update
from app.ui.exec_components import dashboard_status_tag, empty_state, render_html, render_html_table, section_bar
from app.ui.exec_formatters import has_text
from app.ui.pages.common import ensure_sidebar_state


def _timeline_rows(program: dict, latest: dict | None) -> list[dict]:
    milestones = (latest or {}).get("milestones") or []
    if milestones:
        return milestones
    return [
        {"milestone_name": "Program Kickoff", "planned_date": program.get("planned_start_date"), "milestone_status": "Done"},
        {
            "milestone_name": program.get("next_milestone_name") or "Current Milestone",
            "planned_date": program.get("next_milestone_date"),
            "milestone_status": "Current",
        },
        {"milestone_name": "Target Completion", "planned_date": program.get("planned_end_date"), "milestone_status": "Future"},
    ]


def _decision_rows(program: dict, latest: dict | None) -> list[dict]:
    decisions = (latest or {}).get("decisions") or []
    if decisions:
        return [d for d in decisions if not (d.get("decision_topic", "").strip().lower().startswith("no executive decision"))]
    text = (program.get("decision_needed") or "").strip()
    if text and not text.lower().startswith("no "):
        return [{"decision_topic": text}]
    return []


def render() -> None:
    state = ensure_sidebar_state()
    program = get_program(state["selected_program_id"])
    if not program:
        empty_state("Selected program not found.")
        return
    latest = get_latest_submitted_update(str(program["id"]))

    current_status = (latest or {}).get("overall_status") or program.get("current_status") or "Unknown"
    percent = int((latest or {}).get("percent_complete") or program.get("percent_complete") or 0)
    render_html(
        "<div class='weekly-hero'><div class='weekly-hero-top'>"
        f"<div class='weekly-hero-title'>{escape(program.get('name') or 'Program')}</div>"
        f"<div class='weekly-hero-sub'>{escape(program.get('portfolio_name') or 'Portfolio')} • Sponsor: {escape(program.get('sponsor_name') or '—')} • Lead: {escape(program.get('owner_name') or '—')} • PMO</div>"
        "</div>"
        f"<div class='weekly-hero-metrics'><span class='update-pill'>{dashboard_status_tag(current_status)}</span> <span class='update-pill'>{percent}% Complete</span> <span class='update-pill'>{(latest or {}).get('current_phase') or program.get('current_phase') or '—'}</span></div>"
        "<ul><li>Status movement: monitored weekly.</li><li>Percent complete movement: based on latest submitted update.</li><li>Risk exposure movement: based on active portfolio risks.</li></ul>"
        "</div>"
    )

    section_bar("Executive Summary")
    st.write((latest or {}).get("executive_summary") or program.get("summary") or "No summary available.")

    section_bar("Milestone Timeline")
    render_html_table(pd.DataFrame(_timeline_rows(program, latest)), ["milestone_name", "planned_date", "forecast_date", "milestone_status"])

    c1, c2 = st.columns(2)
    with c1:
        section_bar("Recent Accomplishments")
        accomplishments = (latest or {}).get("accomplishments") or ""
        if "," in accomplishments and "\n" not in accomplishments:
            for item in [x.strip() for x in accomplishments.split(",") if x.strip()][:4]:
                st.markdown(f"- {item}")
        else:
            st.write(accomplishments or "No accomplishments logged.")

        section_bar("Upcoming Work")
        st.write((latest or {}).get("next_steps") or program.get("upcoming_work") or "No upcoming work logged.")

    with c2:
        section_bar("Risks / Issues / Dependencies")
        risks = (latest or {}).get("risks") or []
        if not risks and has_text(program.get("risk_detail")):
            risks = [{"severity": "DEP", "description": program.get("risk_detail"), "mitigation": program.get("mitigation"), "target_date": date.today()}]
        order = {"High": 0, "Medium": 1, "Low": 2, "DEP": 3}
        risks = sorted(risks, key=lambda r: order.get(r.get("severity"), 99))
        render_html_table(pd.DataFrame(risks), ["severity", "risk_title", "description", "owner_name", "mitigation", "target_date"])

        section_bar("Leadership Decisions Needed")
        decisions = _decision_rows(program, latest)
        if decisions:
            for i, d in enumerate(decisions, start=1):
                render_html(f"<div class='decision-card'><strong>#{i}</strong> {escape(d.get('decision_topic') or '')}</div>")
        else:
            empty_state("No leadership decisions pending.")

    section_bar("Workstream Status")
    ws = ["Process Design", "Technology Build", "Data Migration", "Change Mgmt", "Testing & Readiness"]
    render_html("<div class='workstream-grid'>" + "".join(f"<div class='ws-card'><strong>{name}</strong><br/>Tracking in weekly cadence.</div>" for name in ws) + "</div>")
