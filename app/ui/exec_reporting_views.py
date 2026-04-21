from __future__ import annotations

from datetime import date, datetime
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


COLORS = {
    "navy": "#11243a",
    "navy_2": "#1b3553",
    "blue": "#2f6fed",
    "blue_soft": "#7ea6f8",
    "panel": "#ffffff",
    "border": "#d5e1ef",
    "text": "#3d556d",
    "muted": "#748aa1",
    "soft": "#f3f7fc",
    "green": "#1f8a57",
    "yellow": "#c5901b",
    "red": "#c25252",
}


def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def metric_card(name: str, value: str | int) -> str:
    return (
        "<div class='dash-kpi'>"
        f"<div class='dash-kpi-name'>{escape(str(name))}</div>"
        f"<div class='dash-kpi-value'>{escape(str(value))}</div>"
        "</div>"
    )


def _status_class(value: str | None) -> str:
    text = (value or "").strip().lower()
    if text in {"green", "on track", "good"}:
        return "dash-tag-green"
    if text in {"amber", "yellow", "at risk"}:
        return "dash-tag-yellow"
    if text in {"red", "critical", "delayed", "off track"}:
        return "dash-tag-red"
    return "dash-tag-neutral"


def dashboard_status_tag(value: str | None) -> str:
    label = (value or "Unknown").upper()
    return f"<span class='update-pill {_status_class(value)}'>{escape(label)}</span>"


def render_html_table(df: pd.DataFrame, columns: list[str]) -> str:
    if df.empty:
        return "<div class='dash-card'><div class='copy'>No records available.</div></div>"
    frame = df[[c for c in columns if c in df.columns]].copy()
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in frame.columns)
    rows: list[str] = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{escape('' if pd.isna(v) else str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    return f"<div class='dash-table'><table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"


def render_dashboard_program_grid(df: pd.DataFrame) -> str:
    cards: list[str] = []
    for row in df.to_dict("records"):
        cards.append(
            "<div class='program-grid-card'>"
            f"<div class='program-grid-head'><div class='program-grid-title'>{escape(str(row.get('Program') or 'Program'))}</div>{dashboard_status_tag(row.get('Status'))}</div>"
            f"<div class='copy'>Sponsor: {escape(str(row.get('Executive Sponsor') or '—'))} • Lead: {escape(str(row.get('Lead') or '—'))}</div>"
            f"<div class='copy'>Phase: {escape(str(row.get('Stage') or '—'))} • Milestone: {escape(str(row.get('Milestone') or '—'))}</div>"
            f"<div class='copy'>Progress: {escape(str(row.get('Progress') or 0))}%</div>"
            "</div>"
        )
    return "<div class='program-grid'>" + "".join(cards) + "</div>"


def render_dashboard_program_grid_section(df: pd.DataFrame) -> None:
    from app.ui.pages.common import open_program

    for idx, row in enumerate(df.to_dict("records")):
        with st.container(border=True):
            render_html(
                f"<div class='program-grid-head'><div class='program-grid-title'>{escape(str(row.get('Program') or 'Program'))}</div>{dashboard_status_tag(row.get('Status'))}</div>"
                f"<div class='copy'>Sponsor: {escape(str(row.get('Executive Sponsor') or '—'))} • Lead: {escape(str(row.get('Lead') or '—'))}</div>"
                f"<div class='copy'>Phase: {escape(str(row.get('Stage') or '—'))} • Milestone: {escape(str(row.get('Milestone') or '—'))}</div>"
                f"<div class='copy'>Progress: {escape(str(row.get('Progress') or 0))}%</div>"
            )
            program_id = str(row.get("program_id") or "")
            if not program_id:
                continue
            if st.button(
                "Open Program",
                key=f"open-program-{program_id}-{idx}",
                type="primary",
            ):
                open_program(program_id)


def render_dashboard_milestones(df: pd.DataFrame) -> str:
    priority_classes = {
        "high": "priority-high",
        "medium": "priority-medium",
        "low": "priority-low",
        "critical": "priority-critical",
    }
    parts: list[str] = []
    for row in df.head(6).to_dict("records"):
        dt = pd.to_datetime(row.get("Milestone Date"), errors="coerce")
        day = dt.strftime("%d") if pd.notna(dt) else "--"
        mon = dt.strftime("%b") if pd.notna(dt) else "TBD"
        priority = str(row.get("Priority") or "Medium")
        priority_class = priority_classes.get(priority.strip().lower(), "priority-neutral")
        parts.append(
            "<div class='milestone-item'>"
            f"<div class='milestone-datebox'><div class='milestone-day'>{day}</div><div class='milestone-month'>{mon}</div></div>"
            "<div>"
            f"<div class='dash-card-heading'>{escape(str(row.get('Program') or ''))}</div>"
            f"<div class='copy'>{escape(str(row.get('Milestone') or ''))}</div>"
            f"<span class='priority-badge {priority_class}'>{escape(priority)}</span>"
            "</div></div>"
        )
    return "<div class='dash-card'>" + "".join(parts) + "</div>"


def risk_trend(value: str | None, escalations: int) -> tuple[str, str]:
    text = (value or "").strip().lower()
    if text in {"red", "critical", "off track", "delayed", "at risk"} or escalations >= 1:
        return "↑ Worse", "risk-trend-worse"
    if text in {"amber", "yellow"}:
        return "↗ Watch", "risk-trend-watch"
    return "→ Stable", "risk-trend-stable"


def render_dashboard_risks(df: pd.DataFrame) -> str:
    parts: list[str] = []
    for row in df.sort_values(by=["Escalations", "Open Risks"], ascending=False).head(6).to_dict("records"):
        escalations = int(row.get("Escalations") or 0)
        trend_label, trend_class = risk_trend(row.get("Status"), escalations)
        severity = str(row.get("Priority") or row.get("Status") or "Medium")
        parts.append(
            "<div class='risk-item risk-card'>"
            "<div class='risk-head'>"
            f"<div class='risk-title'>{escape(str(row.get('Risk Detail') or 'Risk exposure update pending.'))}</div>"
            f"<div class='risk-trend {trend_class}'>{escape(trend_label)}</div>"
            "</div>"
            "<div class='risk-meta-row'>"
            f"<div class='copy'>{escape(str(row.get('Program') or ''))}</div>"
            f"<div class='copy'><strong>Severity:</strong> {escape(severity.title())}</div>"
            "</div>"
            f"<div class='copy risk-meta'><strong>Escalations:</strong> {escape(str(escalations))}</div>"
            "</div>"
        )
    return "<div class='dash-card'>" + "".join(parts) + "</div>"


def render_dashboard_decisions(df: pd.DataFrame) -> str:
    cards: list[str] = []
    for row in df.to_dict("records"):
        cards.append(
            "<div class='decision-card'>"
            f"<div class='dash-card-heading'>{escape(str(row.get('Program') or ''))}</div>"
            f"<div class='copy'>{escape(str(row.get('Decision Needed') or ''))}</div>"
            f"<div class='copy'><strong>Next:</strong> {escape(str(row.get('Next Step') or ''))}</div>"
            "</div>"
        )
    if not cards:
        cards = ["<div class='decision-card'><div class='copy'>No executive decisions pending this cycle.</div></div>"]
    return "<div class='decision-shell'>" + "".join(cards) + "</div>"


def roadmap_stage_segments(stage: str | None) -> list[str]:
    stages = ["Discovery", "Plan", "Execute", "Stabilize", "Value"]
    current = (stage or "Discovery").lower()
    out = []
    for s in stages:
        klass = " active" if s.lower() == current else ""
        out.append(f"<span class='road-band-segment{klass}'>{s}</span>")
    return out


def render_dashboard_roadmap(df: pd.DataFrame) -> str:
    if df.empty:
        return "<div class='roadmap-shell'><div class='copy'>No roadmap data available.</div></div>"
    active_q = "Q3 FY25"
    bands: list[str] = []
    for row in df.head(5).to_dict("records"):
        marker = escape(str(row.get("Milestone") or "Current Milestone"))
        progress = max(4, min(96, int(row.get("Progress") or 0)))
        bands.append(
            "<div class='road-band'>"
            f"<div class='road-band-title'>{escape(str(row.get('Program') or ''))}</div>"
            "<div class='road-band-track'>"
            f"{''.join(roadmap_stage_segments(row.get('Stage')))}"
            f"<div class='road-marker' style='left:{progress}%'></div>"
            "</div>"
            f"<div class='road-marker-label'>{marker}</div>"
            f"<div class='copy road-progress'>{escape(str(progress))}% complete</div>"
            "</div>"
        )
    quarter_tabs = "".join(
        f"<span class='road-quarter{' active' if q == active_q else ''}'>{q}</span>"
        for q in ["Q1 FY25", "Q2 FY25", "Q3 FY25", "Q4 FY25", "Q1 FY26"]
    )
    return "<div class='roadmap-shell'><div class='road-quarter-row'>" + quarter_tabs + "</div>" + "".join(bands) + "</div>"


def cycle_label(reporting_date: date) -> str:
    return reporting_date.strftime("Week Ending %b %d, %Y")


def render_dashboard(
    *,
    portfolio_name: str,
    df: pd.DataFrame,
    reporting_date: date,
    refreshed_at: datetime,
    current_user: object | None,
) -> None:
    display = escape(getattr(current_user, "display_name", None) or getattr(current_user, "email", None) or "Authenticated User")
    render_html(
        "<div class='topbar'>"
        "<div><div class='brand-title'>Portfolio Command Center</div><div class='brand-copy'>Strategic Program Intelligence</div></div>"
        "<div class='search-shell'>Search programs, milestones, risks...</div>"
        "<div class='toolbar-actions'><span class='toolbar-icon'>⚙</span><span class='toolbar-icon'>🔔</span></div>"
        f"<div class='profile-shell'><div><div class='profile-name'>{display}</div><div class='profile-role'>Executive View</div></div><div class='profile-avatar'>{escape(display[:1].upper())}</div></div>"
        "</div>"
    )
    render_html(
        "<div class='dashboard-title-block'>"
        f"<div class='dashboard-title'>{escape(portfolio_name or 'FY25 Strategic Program Intelligence')}</div>"
        f"<div class='dashboard-meta'>{cycle_label(reporting_date)} • <span class='status-pill status-good'>Refreshed {escape(refreshed_at.strftime('%b %d, %Y %I:%M %p ET'))}</span></div>"
        "</div>"
    )

    at_risk = int(df["Status"].astype(str).str.lower().isin(["at risk", "amber", "red", "delayed"]).sum()) if not df.empty else 0
    delayed = int(df["Status"].astype(str).str.lower().isin(["delayed", "red", "off track"]).sum()) if not df.empty else 0
    decisions = int((~df["Decision Needed"].astype(str).str.lower().str.startswith("no ")).sum()) if not df.empty else 0
    avg = int(round(float(df["Progress"].fillna(0).mean()))) if not df.empty else 0
    cols = st.columns(5)
    values = [
        metric_card("TOTAL PROGRAMS", len(df.index)),
        metric_card("AT RISK", at_risk),
        metric_card("DELAYED", delayed),
        metric_card("AVG % COMPLETE", f"{avg}%"),
        metric_card("DECISIONS PENDING", decisions),
    ]
    for col, block in zip(cols, values):
        with col:
            render_html(block)

    st.markdown("<div class='dashboard-main-grid'>", unsafe_allow_html=True)
    left, right = st.columns([1.8, 1])
    with left:
        render_html("<div class='panel-header'><div class='heading'>Program Grid / Weekly Updates</div></div>")
        render_dashboard_program_grid_section(df)
        render_html("<div class='panel-header'><div class='heading'>Portfolio Roadmap / Program Timeline</div></div>")
        render_html(render_dashboard_roadmap(df))
    with right:
        render_html("<div class='panel-header'><div class='heading'>Upcoming Milestones</div></div>")
        upcoming = df[df["Milestone Date"].notna()].copy()
        priority_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        upcoming["_priority_rank"] = (
            upcoming["Priority"].astype(str).str.strip().str.lower().map(priority_order).fillna(1).astype(int)
        )
        upcoming = upcoming.sort_values(by=["Milestone Date", "_priority_rank"]).head(6)
        render_html(render_dashboard_milestones(upcoming))
        render_html("<div class='panel-header'><div class='heading'>Key Risks Across Portfolio</div></div>")
        render_html(render_dashboard_risks(df))
    st.markdown("</div>", unsafe_allow_html=True)

    render_html("<div class='panel-header'><div class='heading'>Executive Action Items / Decisions Needed</div></div>")
    filtered = df[~df["Decision Needed"].astype(str).str.lower().str.startswith("no ")]
    render_html(render_dashboard_decisions(filtered))


def one_pager_status_label(status: str | None) -> str:
    val = (status or "Green").strip().lower()
    if val in {"at risk", "amber", "yellow"}:
        return "AMBER"
    if val in {"red", "delayed", "off track"}:
        return "RED"
    return "GREEN"


def one_pager_status_class(status: str | None) -> str:
    label = one_pager_status_label(status)
    return {"GREEN": "status-green", "AMBER": "status-amber", "RED": "status-red"}[label]


def split_bullets(text: str | None) -> list[str]:
    if not text:
        return []
    if "\n" in text:
        return [t.strip(" -•") for t in text.splitlines() if t.strip()]
    return [t.strip() for t in text.split(";") if t.strip()] or [text]


def one_pager_accomplishments(row: pd.Series) -> str:
    items = "".join(f"<li>{escape(x)}</li>" for x in split_bullets(row.get("Summary")))
    return f"<div class='card'><div class='heading'>Recent Accomplishments</div><ul>{items}</ul></div>"


def one_pager_risks(row: pd.Series) -> str:
    risk = escape(str(row.get("Risk Detail") or "No material risk logged."))
    return (
        "<div class='card'><div class='heading'>Risks / Issues / Dependencies</div>"
        "<table class='risk-matrix'><thead><tr><th>Severity</th><th>Description</th><th>Mitigation</th></tr></thead>"
        f"<tbody><tr><td>{escape(str(row.get('Status') or 'GREEN'))}</td><td>{risk}</td><td>{escape(str(row.get('Mitigation') or '—'))}</td></tr></tbody></table></div>"
    )


def one_pager_decisions(row: pd.Series) -> str:
    return (
        "<div class='card'><div class='heading'>Leadership Decisions Needed</div>"
        f"<div class='decision-card'><div>{escape(str(row.get('Decision Needed') or 'No executive decision required this cycle.'))}</div></div></div>"
    )


def one_pager_workstreams(row: pd.Series) -> str:
    progress = int(row.get("Progress") or 0)
    return (
        "<div class='card'><div class='heading'>Workstream Status</div>"
        "<div class='ws-card'><div class='ws-row'><span class='ws-dot green'></span>Delivery</div><div class='ws-bar'><span style='width:"
        f"{progress}%'></span></div></div>"
        "<div class='ws-card'><div class='ws-row'><span class='ws-dot amber'></span>Technology</div><div class='ws-bar'><span style='width:"
        f"{max(progress-10,0)}%'></span></div></div>"
        "<div class='ws-card'><div class='ws-row'><span class='ws-dot green'></span>Readiness</div><div class='ws-bar'><span style='width:"
        f"{max(progress-5,0)}%'></span></div></div></div>"
    )


def one_pager_milestones(row: pd.Series) -> str:
    progress = max(4, min(96, int(row.get("Progress") or 0)))
    marker = escape(str(row.get("Milestone") or "Current milestone"))
    return (
        "<div class='card'>"
        "<div class='heading'>Milestone Timeline</div>"
        "<div class='road-band-track'>"
        f"{''.join(roadmap_stage_segments(row.get('Stage')))}"
        f"<div class='road-marker' style='left:{progress}%'></div>"
        "</div>"
        f"<div class='road-marker-label'>{marker}</div>"
        "</div>"
    )


def render_program_one_pager(*, portfolio: str, program: str, df: pd.DataFrame, reporting_date: date) -> None:
    row = df.iloc[0] if not df.empty else pd.Series(dtype=object)
    status_label = one_pager_status_label(row.get("Status"))
    status_class = one_pager_status_class(row.get("Status"))
    html = f"""
    <html><head><style>
      body {{margin:0;padding:20px;background:#edf3fb;font-family:Inter,Segoe UI,sans-serif;color:#2b4360;}}
      .hero {{background:linear-gradient(135deg,#10233b,#1b3553);color:white;border-radius:18px;padding:24px;box-shadow:0 20px 40px rgba(16,35,59,.25);}}
      .hero h1 {{margin:0;font-size:2rem;}}
      .hero-sub {{opacity:.9;margin-top:4px;}}
      .hero-grid {{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;}}
      .hero-metric {{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);border-radius:12px;padding:10px;}}
      .status-dot {{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;}}
      .status-green .status-dot {{background:#2fd37a;}} .status-amber .status-dot {{background:#f3bc48;}} .status-red .status-dot {{background:#ef6b6b;}}
      .panel {{background:white;border:1px solid #d6e3f1;border-radius:14px;padding:16px;margin-top:14px;}}
      .panel h3 {{margin:0 0 10px;font-size:1.05rem;}}
      .grid-2 {{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
      .card {{background:white;border:1px solid #d6e3f1;border-radius:14px;padding:14px;}}
      .heading {{font-weight:700;color:#19324d;margin-bottom:8px;}}
      .road-band-track {{ position:relative; display:grid; grid-template-columns:repeat(5,1fr); border-radius:999px; overflow:hidden; margin-top:2px; }}
      .road-band-segment {{ display:block; padding:12px 0; text-align:center; font-weight:700; color:#3d5782; background:#d6dde8; }}
      .road-band-segment:nth-child(1) {{ background:#aebbe8; color:#3754ce; }}
      .road-band-segment:nth-child(2) {{ background:#c0b1e4; color:#6942cc; }}
      .road-band-segment:nth-child(3) {{ background:#3050b5; color:#fff; }}
      .road-band-segment:nth-child(4) {{ background:#abd9ba; color:#1a854f; }}
      .road-band-segment:nth-child(5) {{ background:#d3dae6; color:#7d90a9; }}
      .road-band-segment.active {{ box-shadow: inset 0 0 0 3px rgba(255,255,255,.35); }}
      .road-marker {{ position:absolute; top:-8px; transform:translateX(-50%); width:14px; height:52px; border-radius:4px; background:#2f6fed; }}
      .road-marker-label {{ font-size:1rem; color:#1f4eca; margin-top:8px; font-weight:700; text-align:center; }}
      .decision-card {{background:#f8fbff;border:1px solid #d9e7f6;border-radius:12px;padding:10px;}}
      .risk-matrix {{width:100%;border-collapse:collapse;font-size:.82rem;}} .risk-matrix th,.risk-matrix td {{padding:6px;border-bottom:1px solid #edf3fb;text-align:left;}}
      .ws-card {{margin-bottom:8px;}} .ws-row {{font-size:.85rem;font-weight:600;margin-bottom:5px;}} .ws-dot {{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;}}
      .ws-dot.green{{background:#2fd37a;}} .ws-dot.amber{{background:#f3bc48;}}
      .ws-bar {{height:8px;background:#e8eff8;border-radius:999px;overflow:hidden;}} .ws-bar span {{display:block;height:100%;background:#2f6fed;}}
    </style></head><body>
      <div class='hero'>
        <h1>{escape(program)}</h1>
        <div class='hero-sub'>{escape(portfolio)} • Week Ending {escape(reporting_date.strftime('%b %d, %Y'))}</div>
        <div style='margin-top:10px'>Executive Sponsor: {escape(str(row.get('Executive Sponsor') or '—'))} • Program Lead: {escape(str(row.get('Lead') or '—'))} • PMO</div>
        <div class='hero-grid'>
          <div class='hero-metric {status_class}'><span class='status-dot'></span>Overall Status: {status_label}</div>
          <div class='hero-metric'>% Complete: {escape(str(row.get('Progress') or 0))}%</div>
          <div class='hero-metric'>Current Phase: {escape(str(row.get('Stage') or 'Discovery'))}</div>
        </div>
      </div>
      <div class='panel'><h3>Executive Summary</h3><div>{escape(str(row.get('Summary') or 'No summary available.'))}</div></div>
      {one_pager_milestones(row)}
      <div class='grid-2'>
        {one_pager_accomplishments(row)}
        <div class='card'><div class='heading'>Upcoming Work (Next 2 Weeks)</div><div>{escape(str(row.get('Upcoming Work') or 'No upcoming work logged.'))}</div></div>
      </div>
      <div class='grid-2'>
        {one_pager_risks(row)}
        {one_pager_decisions(row)}
      </div>
      {one_pager_workstreams(row)}
    </body></html>
    """
    components.html(html, height=2450, scrolling=True)
