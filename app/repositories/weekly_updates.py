from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import text

from app.db import connection, fetch_all, fetch_one


STATUS_OPTIONS = {"On Track", "Needs Attention", "At Risk"}
PHASE_OPTIONS = {"Discovery", "Phase 1", "Phase 2", "Phase 3", "Phase 4"}
TREND_OPTIONS = {"Up", "Flat", "Down"}
RISK_SEVERITY_OPTIONS = {"High", "Medium", "Low", "DEP"}


def _validate_payload(payload: dict[str, Any]) -> None:
    if not (0 <= int(payload["percent_complete"]) <= 100):
        raise ValueError("Percent complete must be between 0 and 100")
    if payload["overall_status"] not in STATUS_OPTIONS:
        raise ValueError("Invalid status")
    if payload["current_phase"] not in PHASE_OPTIONS:
        raise ValueError("Invalid phase")
    if payload["trend"] not in TREND_OPTIONS:
        raise ValueError("Invalid trend")
    for risk in payload.get("risks", []):
        if risk.get("severity") not in RISK_SEVERITY_OPTIONS:
            raise ValueError("Invalid risk severity")


def get_weekly_update(program_id: str, week_ending: date) -> dict | None:
    return fetch_one(
        """
        SELECT id, program_id, week_ending, update_status,
               overall_status, current_phase, percent_complete, trend,
               accomplishments, dependencies, next_steps, executive_summary,
               submitted_at, submitted_by
        FROM weekly_update
        WHERE program_id = :program_id AND week_ending = :week_ending
        """,
        {"program_id": program_id, "week_ending": week_ending},
    )


def list_milestones(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT milestone_name, planned_date, forecast_date, status, comment, sort_order
        FROM weekly_update_milestone
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def list_risks(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT severity, risk_title, owner_name, target_date, description, mitigation, sort_order
        FROM weekly_update_risk
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def list_decisions(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT decision_topic, required_by, impact_if_unresolved, recommendation, sort_order
        FROM weekly_update_decision
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def _upsert_weekly_update(conn, payload: dict[str, Any], update_status: str) -> str:
    result = conn.execute(
        text(
            """
            INSERT INTO weekly_update (
                program_id, week_ending, update_status, overall_status, current_phase,
                percent_complete, trend, accomplishments, dependencies, next_steps,
                executive_summary, submitted_at, submitted_by, updated_at
            ) VALUES (
                :program_id, :week_ending, :update_status, :overall_status, :current_phase,
                :percent_complete, :trend, :accomplishments, :dependencies, :next_steps,
                :executive_summary, :submitted_at, :submitted_by, :updated_at
            )
            ON CONFLICT (program_id, week_ending) DO UPDATE SET
                update_status = EXCLUDED.update_status,
                overall_status = EXCLUDED.overall_status,
                current_phase = EXCLUDED.current_phase,
                percent_complete = EXCLUDED.percent_complete,
                trend = EXCLUDED.trend,
                accomplishments = EXCLUDED.accomplishments,
                dependencies = EXCLUDED.dependencies,
                next_steps = EXCLUDED.next_steps,
                executive_summary = EXCLUDED.executive_summary,
                submitted_at = EXCLUDED.submitted_at,
                submitted_by = EXCLUDED.submitted_by,
                updated_at = EXCLUDED.updated_at
            RETURNING id
            """
        ),
        {
            "program_id": payload["program_id"],
            "week_ending": payload["week_ending"],
            "update_status": update_status,
            "overall_status": payload["overall_status"],
            "current_phase": payload["current_phase"],
            "percent_complete": payload["percent_complete"],
            "trend": payload["trend"],
            "accomplishments": payload.get("accomplishments"),
            "dependencies": payload.get("dependencies"),
            "next_steps": payload.get("next_steps"),
            "executive_summary": payload.get("executive_summary"),
            "submitted_at": datetime.utcnow() if update_status == "submitted" else None,
            "submitted_by": payload.get("submitted_by") if update_status == "submitted" else None,
            "updated_at": datetime.utcnow(),
        },
    )
    return str(result.scalar_one())


def _replace_children(conn, weekly_update_id: str, payload: dict[str, Any]) -> None:
    conn.execute(text("DELETE FROM weekly_update_milestone WHERE weekly_update_id = :id"), {"id": weekly_update_id})
    conn.execute(text("DELETE FROM weekly_update_risk WHERE weekly_update_id = :id"), {"id": weekly_update_id})
    conn.execute(text("DELETE FROM weekly_update_decision WHERE weekly_update_id = :id"), {"id": weekly_update_id})

    for i, milestone in enumerate(payload.get("milestones", []), start=1):
        conn.execute(
            text(
                """
                INSERT INTO weekly_update_milestone (
                    weekly_update_id, sort_order, milestone_name, planned_date,
                    forecast_date, status, comment
                ) VALUES (
                    :weekly_update_id, :sort_order, :milestone_name, :planned_date,
                    :forecast_date, :status, :comment
                )
                """
            ),
            {"weekly_update_id": weekly_update_id, "sort_order": i, **milestone},
        )

    for i, risk in enumerate(payload.get("risks", []), start=1):
        conn.execute(
            text(
                """
                INSERT INTO weekly_update_risk (
                    weekly_update_id, sort_order, severity, risk_title, owner_name,
                    target_date, description, mitigation
                ) VALUES (
                    :weekly_update_id, :sort_order, :severity, :risk_title, :owner_name,
                    :target_date, :description, :mitigation
                )
                """
            ),
            {"weekly_update_id": weekly_update_id, "sort_order": i, **risk},
        )

    for i, decision in enumerate(payload.get("decisions", []), start=1):
        conn.execute(
            text(
                """
                INSERT INTO weekly_update_decision (
                    weekly_update_id, sort_order, decision_topic, required_by,
                    impact_if_unresolved, recommendation
                ) VALUES (
                    :weekly_update_id, :sort_order, :decision_topic, :required_by,
                    :impact_if_unresolved, :recommendation
                )
                """
            ),
            {"weekly_update_id": weekly_update_id, "sort_order": i, **decision},
        )


def save_weekly_update_draft(payload: dict[str, Any]) -> str:
    _validate_payload(payload)
    with connection() as conn:
        weekly_update_id = _upsert_weekly_update(conn, payload, "draft")
        _replace_children(conn, weekly_update_id, payload)
    return weekly_update_id


def submit_weekly_update(payload: dict[str, Any]) -> str:
    _validate_payload(payload)
    with connection() as conn:
        weekly_update_id = _upsert_weekly_update(conn, payload, "submitted")
        _replace_children(conn, weekly_update_id, payload)
        conn.execute(
            text("SELECT publish_weekly_update(:weekly_update_id, :submitted_by_user_id)"),
            {
                "weekly_update_id": weekly_update_id,
                "submitted_by_user_id": payload.get("submitted_by"),
            },
        )
    return weekly_update_id


def reset_weekly_update(program_id: str, week_ending: date) -> dict | None:
    update = get_weekly_update(program_id, week_ending)
    if not update:
        return None
    return {
        **update,
        "milestones": list_milestones(update["id"]),
        "risks": list_risks(update["id"]),
        "decisions": list_decisions(update["id"]),
    }


def get_latest_submitted_update(program_id: str) -> dict | None:
    update = fetch_one(
        """
        SELECT id, program_id, week_ending, overall_status, current_phase,
               percent_complete, trend, accomplishments, dependencies,
               next_steps, executive_summary
        FROM weekly_update
        WHERE program_id = :program_id AND update_status = 'submitted'
        ORDER BY week_ending DESC
        LIMIT 1
        """,
        {"program_id": program_id},
    )
    if not update:
        return None
    return {
        **update,
        "milestones": list_milestones(update["id"]),
        "risks": list_risks(update["id"]),
        "decisions": list_decisions(update["id"]),
    }
