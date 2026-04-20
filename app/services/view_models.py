from __future__ import annotations

from datetime import date

from app.ui.exec_formatters import has_text, severity_rank


def build_portfolio_kpis(programs: list[dict]) -> dict:
    total = len(programs)
    at_risk = sum(1 for p in programs if (p.get("current_status") or "") == "At Risk")
    needs_attention = sum(1 for p in programs if (p.get("current_status") or "") == "Needs Attention")
    avg_complete = round(sum((p.get("percent_complete") or 0) for p in programs) / max(total, 1), 1)
    decisions_pending = sum(
        1
        for p in programs
        if has_text(p.get("decision_needed"))
        and not (p.get("decision_needed") or "").strip().lower().startswith("no ")
        and not (p.get("decision_needed") or "").strip().lower().startswith("no executive decision")
    )
    return {
        "total": total,
        "at_risk": at_risk,
        "needs_attention": needs_attention,
        "avg_complete": avg_complete,
        "decisions_pending": decisions_pending,
    }


def rank_program_risks(programs: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for p in programs:
        risk = (p.get("risk_detail") or "").strip()
        if risk:
            rows.append(
                {
                    "program": p["name"],
                    "risk": risk,
                    "mitigation": p.get("mitigation") or "—",
                    "severity": "High" if (p.get("current_status") == "At Risk") else "Medium",
                }
            )
    rows.sort(key=lambda r: (severity_rank(r.get("severity")), r["program"]))
    return rows


def build_signal_cards(program: dict, latest: dict | None) -> list[tuple[str, str]]:
    milestone_count = len((latest or {}).get("milestones", []))
    risk_count = len((latest or {}).get("risks", []))
    decision_count = len((latest or {}).get("decisions", []))
    percent = int(program.get("percent_complete") or 0)
    return [
        ("Delivery Progress", f"{percent}%"),
        ("Milestone Readiness", "Good" if milestone_count > 0 else "Needs Input"),
        ("Risk Pressure", "High" if risk_count > 2 else "Moderate" if risk_count else "Low"),
        ("Decision Readiness", "Pending" if decision_count else "Clear"),
        ("Trend / Execution Signal", (latest or {}).get("trend") or "Flat"),
    ]


def sort_milestones(rows: list[dict]) -> list[dict]:
    def keyf(row: dict):
        forecast = row.get("forecast_date")
        planned = row.get("planned_date")
        return (forecast is None, forecast or planned or date.max, row.get("sort_order") or 9999)

    return sorted(rows, key=keyf)
