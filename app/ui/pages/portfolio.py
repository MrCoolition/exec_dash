from __future__ import annotations

import datetime as dt
from html import escape
from zoneinfo import ZoneInfo

import streamlit as st

from app.repositories.programs import list_program_snapshots_by_portfolio
from app.services.exec_reporting_adapter import build_exec_dataframe
from app.services.view_models import build_portfolio_kpis
from app.ui.exec_components import (
    dashboard_status_tag,
    empty_state,
    metric_card,
    render_html,
    render_html_table,
    section_bar,
)
from app.ui.exec_formatters import has_text
from app.ui.pages.common import ensure_sidebar_state, open_program


def _decision_pending(value: str | None) -> bool:
    if not has_text(value):
        return False
    normalized = (value or "").strip().lower()
    return not (normalized.startswith("no ") or normalized.startswith("no executive decision"))


def render() -> None:
    state = ensure_sidebar_state()
    portfolio = state.get("selected_portfolio")
    if not portfolio:
        empty_state("No portfolio selected. Choose a program from the sidebar.")
        return

    programs = list_program_snapshots_by_portfolio(str(portfolio["id"]))
    df = build_exec_dataframe(programs)

    user = st.session_state.get("user")
    display_name = escape(getattr(user, "display_name", None) or getattr(user, "email", None) or "Authenticated User")
    render_html(
        "<div class='topbar'>"
        "<div class='brand-block'><div class='brand-title'>Portfolio Command Center</div><div class='brand-copy'>Strategic Program Intelligence</div></div>"
        "<div class='search-shell'>Search programs, milestones, risks...</div>"
        "<div class='toolbar-actions'><span class='toolbar-icon'>⚙️</span><span class='toolbar-icon'>🔔</span></div>"
        f"<div class='profile-shell'><div class='profile-copy'><div class='profile-name'>{display_name}</div><div class='profile-role'>Signed in</div></div><div class='profile-avatar'>{display_name[:1].upper()}</div></div>"
        "</div>"
    )

    refreshed = dt.datetime.now(ZoneInfo("America/New_York")).strftime("%b %d, %Y %I:%M %p ET")
    reporting_date = state["reporting_date"].strftime("%b %d, %Y")
    render_html(
        "<div class='dashboard-title-block'>"
        "<div class='dashboard-title'>FY25 Strategic Transformation Portfolio</div>"
        f"<div class='dashboard-meta'>Week Ending {reporting_date} • Refreshed {refreshed}</div></div>"
    )

    kpi = build_portfolio_kpis(programs)
    kpi["decisions_pending"] = sum(1 for p in programs if _decision_pending(p.get("decision_needed")))
    cols = st.columns(5)
    for col, html in zip(
        cols,
        [
            metric_card("Total Programs", kpi["total"]),
            metric_card("At Risk", kpi["at_risk"]),
            metric_card("Delayed / Needs Attention", kpi["needs_attention"]),
            metric_card("Avg % Complete", f"{kpi['avg_complete']}%"),
            metric_card("Decisions Pending", kpi["decisions_pending"]),
        ],
    ):
        with col:
            render_html(html)

    if df.empty:
        empty_state("No active programs are available for this portfolio yet.")
        return

    left, right = st.columns([1.7, 1])
    with left:
        section_bar("Program Grid / Weekly Updates")
        card_df = df.sort_values(by=["Milestone Date", "Program"], na_position="last")
        for row in card_df.to_dict("records"):
            with st.container(border=True):
                st.markdown(f"**{row['Program']}**  {dashboard_status_tag(row['Status'])}", unsafe_allow_html=True)
                st.caption(row.get("Status Note") or row.get("Summary"))
                st.caption(f"Milestone: {row.get('Milestone')} • {row.get('Milestone Date')}")
                if st.button("Open Program", key=f"program-card-{row['program_id']}"):
                    open_program(str(row["program_id"]))

        section_bar("Portfolio Roadmap")
        stages = ["Discover", "Plan", "Execute", "Stabilize", "Value"]
        render_html(
            "<div class='dash-card'><div class='roadmap-grid'>"
            + "".join(f"<div class='road-band'>{s}<div class='road-marker'>Portfolio stage</div></div>" for s in stages)
            + "</div></div>"
        )

    with right:
        section_bar("Upcoming Milestones")
        upcoming = card_df[card_df["Milestone Date"].notna()].head(5)
        render_html_table(upcoming, ["Program", "Milestone", "Milestone Date", "Status"])

        section_bar("Key Risks Across Portfolio")
        risks = card_df.sort_values(by=["Escalations", "Open Risks"], ascending=False).head(5)
        render_html_table(risks, ["Program", "Open Risks", "Escalations", "Risk Detail"])

    section_bar("Executive Action Items / Decisions Needed")
    decisions = card_df[card_df["Decision Needed"].apply(_decision_pending)]
    render_html_table(decisions, ["Program", "Decision Needed", "Next Step", "Status"])
