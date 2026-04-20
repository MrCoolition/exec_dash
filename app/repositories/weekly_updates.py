from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from app.db import _to_psycopg2_query, connection, fetch_all, fetch_one
from app.ui.exec_formatters import has_text


STATUS_OPTIONS = {"On Track", "Needs Attention", "At Risk"}
PHASE_OPTIONS = {"Discovery", "Phase 1", "Phase 2", "Phase 3", "Phase 4"}
TREND_OPTIONS = {"Up", "Flat", "Down"}
RISK_SEVERITY_OPTIONS = {"High", "Medium", "Low", "DEP"}


def resolve_app_user_id(auth_subject: str | None, email: str | None) -> str | None:
    row = fetch_one(
        """
        SELECT user_id::text AS user_id
        FROM app.app_user
        WHERE (:auth_subject IS NOT NULL AND auth_subject = :auth_subject)
           OR (:email IS NOT NULL AND email = :email)
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        {"auth_subject": auth_subject, "email": email},
    )
    return row["user_id"] if row else None


def _clean_milestones(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        if has_text(row.get("milestone_name")) or row.get("planned_date") or row.get("forecast_date"):
            milestone_name = (row.get("milestone_name") or "").strip()
            if not milestone_name:
                continue
            cleaned.append(
                {
                    "milestone_name": milestone_name,
                    "planned_date": row.get("planned_date"),
                    "forecast_date": row.get("forecast_date"),
                    "milestone_status": (row.get("status") or "").strip() or None,
                    "comment": (row.get("comment") or "").strip() or None,
                }
            )
    return cleaned


def _clean_risks(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        if has_text(row.get("risk_title")) or has_text(row.get("description")):
            severity = (row.get("severity") or "").strip()
            title = (row.get("risk_title") or "").strip()
            if not severity or not title:
                continue
            cleaned.append(
                {
                    "severity": severity,
                    "title": title,
                    "owner_name": (row.get("owner_name") or "").strip() or None,
                    "target_date": row.get("target_date"),
                    "description": (row.get("description") or "").strip() or None,
                    "mitigation_plan": (row.get("mitigation") or "").strip() or None,
                }
            )
    return cleaned


def _clean_decisions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        if has_text(row.get("decision_topic")):
            cleaned.append(
                {
                    "decision_topic": (row.get("decision_topic") or "").strip(),
                    "required_by": row.get("required_by"),
                    "impact_if_unresolved": (row.get("impact_if_unresolved") or "").strip() or None,
                    "recommendation": (row.get("recommendation") or "").strip() or None,
                }
            )
    return cleaned


def _validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not (0 <= int(payload["percent_complete"]) <= 100):
        raise ValueError("Percent complete must be between 0 and 100")
    if payload["overall_status"] not in STATUS_OPTIONS:
        raise ValueError("Invalid status")
    if payload["current_phase"] not in PHASE_OPTIONS:
        raise ValueError("Invalid phase")
    if payload["trend"] not in TREND_OPTIONS:
        raise ValueError("Invalid trend")

    payload = {**payload}
    payload["milestones"] = _clean_milestones(payload.get("milestones", []))
    payload["risks"] = _clean_risks(payload.get("risks", []))
    payload["decisions"] = _clean_decisions(payload.get("decisions", []))

    for risk in payload.get("risks", []):
        if risk.get("severity") and risk.get("severity") not in RISK_SEVERITY_OPTIONS:
            raise ValueError("Invalid risk severity")
    return payload


def get_weekly_update(program_id: str, week_ending: date) -> dict | None:
    return fetch_one(
        """
        SELECT weekly_update_id AS id, program_id, week_ending, update_state AS update_status,
               overall_status, current_phase, percent_complete, trend,
               accomplishments, dependencies, next_steps, executive_summary,
               submitted_at, updated_at, submitted_by_user_id::text AS submitted_by
        FROM app.weekly_update
        WHERE program_id = :program_id AND week_ending = :week_ending
        """,
        {"program_id": program_id, "week_ending": week_ending},
    )


def list_milestones(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT milestone_name, planned_date, forecast_date, milestone_status AS status, comment, sort_order
        FROM app.weekly_update_milestone
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def list_risks(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT severity, title AS risk_title, owner_name, target_date, description, mitigation_plan AS mitigation, sort_order
        FROM app.weekly_update_risk
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def list_decisions(weekly_update_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT decision_topic, required_by, impact_if_unresolved, recommendation, sort_order
        FROM app.weekly_update_decision
        WHERE weekly_update_id = :weekly_update_id
        ORDER BY sort_order
        """,
        {"weekly_update_id": weekly_update_id},
    )


def _as_uuid_or_none(raw_value: str | None) -> str | None:
    if not raw_value:
        return None
    try:
        return str(UUID(raw_value))
    except (ValueError, TypeError, AttributeError):
        return None


def _upsert_weekly_update(conn, payload: dict[str, Any], update_status: str) -> str:
    user_id = _as_uuid_or_none(payload.get("submitted_by"))
    with conn.cursor() as cursor:
        cursor.execute(
            _to_psycopg2_query(
                """
                INSERT INTO app.weekly_update (
                    program_id, week_ending, update_state, overall_status, current_phase,
                    percent_complete, trend, accomplishments, dependencies, next_steps,
                    executive_summary, submitted_at, submitted_by_user_id, updated_by_user_id, updated_at
                ) VALUES (
                    :program_id, :week_ending, :update_status, :overall_status, :current_phase,
                    :percent_complete, :trend, :accomplishments, :dependencies, :next_steps,
                    :executive_summary, :submitted_at, :submitted_by, :updated_by, :updated_at
                )
                ON CONFLICT (program_id, week_ending) DO UPDATE SET
                    update_state = EXCLUDED.update_state,
                    overall_status = EXCLUDED.overall_status,
                    current_phase = EXCLUDED.current_phase,
                    percent_complete = EXCLUDED.percent_complete,
                    trend = EXCLUDED.trend,
                    accomplishments = EXCLUDED.accomplishments,
                    dependencies = EXCLUDED.dependencies,
                    next_steps = EXCLUDED.next_steps,
                    executive_summary = EXCLUDED.executive_summary,
                    submitted_at = EXCLUDED.submitted_at,
                    submitted_by_user_id = EXCLUDED.submitted_by_user_id,
                    updated_by_user_id = EXCLUDED.updated_by_user_id,
                    updated_at = EXCLUDED.updated_at
                RETURNING weekly_update_id
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
                "submitted_by": user_id if update_status == "submitted" else None,
                "updated_by": user_id,
                "updated_at": datetime.utcnow(),
            },
        )
        row = cursor.fetchone()
    if row is None:
        raise RuntimeError("Failed to upsert weekly update")
    return str(row[0])


def _replace_children(conn, weekly_update_id: str, payload: dict[str, Any]) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            _to_psycopg2_query("DELETE FROM app.weekly_update_milestone WHERE weekly_update_id = :id"),
            {"id": weekly_update_id},
        )
        cursor.execute(
            _to_psycopg2_query("DELETE FROM app.weekly_update_risk WHERE weekly_update_id = :id"),
            {"id": weekly_update_id},
        )
        cursor.execute(
            _to_psycopg2_query("DELETE FROM app.weekly_update_decision WHERE weekly_update_id = :id"),
            {"id": weekly_update_id},
        )

        for i, milestone in enumerate(payload.get("milestones", []), start=1):
            cursor.execute(
                _to_psycopg2_query(
                    """
                    INSERT INTO app.weekly_update_milestone (
                        weekly_update_id, sort_order, milestone_name, planned_date,
                        forecast_date, milestone_status, comment
                    ) VALUES (
                        :weekly_update_id, :sort_order, :milestone_name, :planned_date,
                        :forecast_date, :milestone_status, :comment
                    )
                    """
                ),
                {"weekly_update_id": weekly_update_id, "sort_order": i, **milestone},
            )

        for i, risk in enumerate(payload.get("risks", []), start=1):
            cursor.execute(
                _to_psycopg2_query(
                    """
                    INSERT INTO app.weekly_update_risk (
                        weekly_update_id, sort_order, severity, title, owner_name,
                        target_date, description, mitigation_plan
                    ) VALUES (
                        :weekly_update_id, :sort_order, :severity, :title, :owner_name,
                        :target_date, :description, :mitigation_plan
                    )
                    """
                ),
                {"weekly_update_id": weekly_update_id, "sort_order": i, **risk},
            )

        for i, decision in enumerate(payload.get("decisions", []), start=1):
            cursor.execute(
                _to_psycopg2_query(
                    """
                    INSERT INTO app.weekly_update_decision (
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
    payload = _validate_payload(payload)
    with connection() as conn:
        weekly_update_id = _upsert_weekly_update(conn, payload, "draft")
        _replace_children(conn, weekly_update_id, payload)
    return weekly_update_id


def submit_weekly_update(payload: dict[str, Any]) -> str:
    payload = _validate_payload(payload)
    with connection() as conn:
        weekly_update_id = _upsert_weekly_update(conn, payload, "submitted")
        _replace_children(conn, weekly_update_id, payload)
        with conn.cursor() as cursor:
            cursor.execute(
                _to_psycopg2_query("SELECT app.publish_weekly_update(:weekly_update_id, :submitted_by_user_id)"),
                {
                    "weekly_update_id": weekly_update_id,
                    "submitted_by_user_id": _as_uuid_or_none(payload.get("submitted_by")),
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
        SELECT weekly_update_id AS id,
               program_id,
               week_ending,
               overall_status,
               current_phase,
               percent_complete, trend, accomplishments, dependencies,
               next_steps, executive_summary, submitted_at, updated_at
        FROM app.v_latest_submitted_update
        WHERE program_id = :program_id AND update_state = 'submitted'
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
