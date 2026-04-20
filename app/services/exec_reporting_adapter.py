from __future__ import annotations

import pandas as pd


def build_exec_dataframe(programs: list[dict]) -> pd.DataFrame:
    rows = []
    for p in programs:
        rows.append(
            {
                "Program": p.get("name") or "—",
                "Executive Sponsor": p.get("sponsor_name") or "—",
                "Lead": p.get("owner_name") or "—",
                "Stage": p.get("current_phase") or "Discovery",
                "Status": p.get("current_status") or "On Track",
                "Priority": p.get("priority") or "Medium",
                "Start": p.get("planned_start_date"),
                "End": p.get("planned_end_date"),
                "Progress": int(p.get("percent_complete") or 0),
                "Milestone": p.get("next_milestone_name") or "—",
                "Milestone Date": p.get("next_milestone_date"),
                "Delivery Health": p.get("delivery_health") or "Green",
                "Tech Health": p.get("tech_health") or "Green",
                "Team Health": p.get("team_health") or "Green",
                "Open Risks": int(p.get("open_risks_count") or 0),
                "Escalations": int(p.get("escalations_count") or 0),
                "Summary": p.get("summary") or "No summary available.",
                "Upcoming Work": p.get("upcoming_work") or "No upcoming work logged.",
                "Risk Detail": p.get("risk_detail") or "No material risk logged.",
                "Decision Needed": p.get("decision_needed") or "No executive decision required this cycle.",
                "Mitigation": p.get("mitigation") or "No mitigation required.",
                "Status Note": p.get("status_note") or p.get("summary") or "No status note.",
                "Next Step": p.get("next_step") or p.get("upcoming_work") or "No next step logged.",
                "program_id": str(p.get("id")),
                "portfolio_id": str(p.get("portfolio_id")),
            }
        )
    df = pd.DataFrame(rows)
    for col in ["Start", "End", "Milestone Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df
