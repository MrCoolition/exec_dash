import datetime as dt

from app.repositories import weekly_updates
from app.services.user_context import UserContext
from app.models.pydantic_models import User
from app.ui.pages import update_center


def test_clean_decisions_drops_blank_rows():
    rows = [
        {"decision_topic": "", "required_by": None},
        {"decision_topic": "   ", "required_by": None},
        {"decision_topic": "Approve budget", "required_by": None},
    ]
    cleaned = weekly_updates._clean_decisions(rows)
    assert len(cleaned) == 1
    assert cleaned[0]["decision_topic"] == "Approve budget"


def test_submitted_by_resolution_uses_app_user_lookup(monkeypatch):
    ctx = UserContext(user=User(provider="auth0", provider_sub="sub-1", email="leader@example.com"), role_codes={"user"}, tenant_slugs=["default"])

    monkeypatch.setattr(update_center, "resolve_app_user_id", lambda auth_subject, email: "11111111-1111-1111-1111-111111111111")
    assert update_center._submitted_by(ctx) == "11111111-1111-1111-1111-111111111111"


def test_portfolio_decision_counts_ignore_blank():
    programs = [
        {"decision_needed": ""},
        {"decision_needed": "   "},
        {"decision_needed": None},
        {"decision_needed": "Need EVP approval"},
    ]
    from app.services.view_models import build_portfolio_kpis

    kpi = build_portfolio_kpis(programs)
    assert kpi["decisions_pending"] == 1


def test_readiness_requires_summary_accomplishments_and_milestone():
    issues = update_center._readiness(
        {
            "executive_summary": "",
            "accomplishments": "",
            "milestones": [],
        }
    )
    assert issues == ["Executive Summary Notes", "Key Accomplishments This Week", "At least one milestone"]


def test_summary_sentence_contains_program_progress_trend_and_week():
    sentence = update_center._summary_sentence(
        "Program A",
        {"percent_complete": 42, "trend": "Up", "week_ending": dt.date(2026, 4, 17)},
    )
    assert "Program A" in sentence
    assert "42%" in sentence
    assert "Up" in sentence
    assert "2026-04-17" in sentence
