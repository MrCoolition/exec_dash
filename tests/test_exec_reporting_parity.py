from datetime import date

from app.repositories import weekly_updates
from app.services.exec_reporting_adapter import build_exec_dataframe
from app.services.view_models import build_portfolio_kpis


def test_exec_dataframe_maps_expected_fields():
    df = build_exec_dataframe([
        {"id": "p1", "portfolio_id": "pf1", "name": "Program A", "percent_complete": 45, "planned_start_date": "2026-01-01"}
    ])
    assert list(df["Program"])[0] == "Program A"
    assert list(df["Progress"])[0] == 45
    assert "Milestone Date" in df.columns


def test_decision_pending_kpi_ignores_no_prefix():
    programs = [{"decision_needed": "No decision"}, {"decision_needed": "No executive decision required"}, {"decision_needed": "Approve scope"}]
    assert build_portfolio_kpis(programs)["decisions_pending"] == 1


def test_clean_payload_filters_invalid_child_rows():
    payload = {
        "percent_complete": 55,
        "overall_status": "On Track",
        "current_phase": "Phase 1",
        "trend": "Flat",
        "milestones": [{"milestone_name": "", "planned_date": date.today()}],
        "risks": [{"severity": "", "risk_title": "Missing severity"}, {"severity": "High", "risk_title": "Valid"}],
        "decisions": [{"decision_topic": ""}, {"decision_topic": "Need approval"}],
    }
    cleaned = weekly_updates._validate_payload(payload)
    assert cleaned["milestones"] == []
    assert len(cleaned["risks"]) == 1
    assert len(cleaned["decisions"]) == 1


def test_submit_uses_schema_qualified_publish_call(monkeypatch):
    calls: list[str] = []

    class FakeCursor:
        def execute(self, query, params=None):
            calls.append(query)

        def fetchone(self):
            return ["wu-id"]

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    class FakeConn:
        def cursor(self):
            return FakeCursor()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(weekly_updates, "connection", lambda: FakeConn())
    monkeypatch.setattr(weekly_updates, "_to_psycopg2_query", lambda q: q)

    payload = {
        "program_id": "p1",
        "week_ending": date.today(),
        "overall_status": "On Track",
        "current_phase": "Phase 1",
        "percent_complete": 50,
        "trend": "Flat",
        "accomplishments": "a",
        "dependencies": "d",
        "next_steps": "n",
        "executive_summary": "e",
        "milestones": [],
        "risks": [],
        "decisions": [],
        "submitted_by": None,
    }
    weekly_updates.submit_weekly_update(payload)
    assert any("SELECT app.publish_weekly_update" in q for q in calls)
