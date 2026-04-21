from __future__ import annotations

import pandas as pd


def _first(row: dict, *keys: str, default=None):
    for key in keys:
        if key in row and row.get(key) not in (None, ""):
            return row.get(key)
    return default


def build_exec_dataframe(programs: list[dict]) -> pd.DataFrame:
    rows = []
    for p in programs:
        rows.append(
            {
                "Program": _first(p, "program_name", "name", default="—"),
                "Executive Sponsor": _first(p, "executive_sponsor", "sponsor_name", default="—"),
                "Lead": _first(p, "program_lead", "owner_name", default="—"),
                "Stage": _first(p, "current_phase", default="Discovery"),
                "Status": _first(p, "current_status", default="On Track"),
                "Priority": _first(p, "priority", default="Medium"),
                "Start": _first(p, "planned_start_date"),
                "End": _first(p, "planned_end_date"),
                "Progress": int(_first(p, "percent_complete", default=0) or 0),
                "Milestone": _first(p, "current_milestone_name", "next_milestone_name", default="—"),
                "Milestone Date": _first(p, "current_milestone_date", "next_milestone_date"),
                "Delivery Health": _first(p, "delivery_health", default="Green"),
                "Tech Health": _first(p, "tech_health", default="Green"),
                "Team Health": _first(p, "team_health", default="Green"),
                "Open Risks": int(_first(p, "open_risks_count", default=0) or 0),
                "Escalations": int(_first(p, "escalations_count", default=0) or 0),
                "Summary": _first(p, "summary", default="No summary available."),
                "Upcoming Work": _first(p, "upcoming_work", default="No upcoming work logged."),
                "Risk Detail": _first(p, "risk_detail", default="No material risk logged."),
                "Decision Needed": _first(p, "decision_needed", default="No executive decision required this cycle."),
                "Mitigation": _first(p, "mitigation", default="No mitigation required."),
                "Status Note": _first(p, "status_note", "summary", default="No status note."),
                "Next Step": _first(p, "next_step", "upcoming_work", default="No next step logged."),
                "program_id": str(_first(p, "program_id", "id", default="")),
                "portfolio_id": str(_first(p, "portfolio_id", default="")),
                "portfolio_name": _first(p, "portfolio_name", default=""),
            }
        )
    df = pd.DataFrame(rows)
    for col in ["Start", "End", "Milestone Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
