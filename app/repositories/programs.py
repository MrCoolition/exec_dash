from __future__ import annotations

from app.db import fetch_all, fetch_one


def list_programs() -> list[dict]:
    return fetch_all(
        """
        SELECT program_id AS id,
               portfolio_id,
               program_name AS name,
               executive_sponsor AS sponsor_name,
               program_lead AS owner_name,
               current_status, current_phase, percent_complete,
               current_milestone_name AS next_milestone_name,
               current_milestone_date AS next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count,
               portfolio_name AS portfolio_name,
               priority,
               planned_start_date,
               planned_end_date,
               delivery_health,
               tech_health,
               team_health,
               last_submitted_update_id,
               created_at,
               updated_at
        FROM app.v_program_current_snapshot
        WHERE COALESCE(is_active, TRUE)
        ORDER BY program_name
        """
    )


def get_program(program_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT program_id AS id,
               portfolio_id,
               program_name AS name,
               executive_sponsor AS sponsor_name,
               program_lead AS owner_name,
               current_status, current_phase, percent_complete,
               current_milestone_name AS next_milestone_name,
               current_milestone_date AS next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count,
               portfolio_name AS portfolio_name,
               priority,
               planned_start_date,
               planned_end_date,
               delivery_health,
               tech_health,
               team_health,
               last_submitted_update_id,
               created_at,
               updated_at
        FROM app.v_program_current_snapshot
        WHERE program_id = :program_id
        """,
        {"program_id": program_id},
    )


def list_program_snapshots_by_portfolio(portfolio_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT program_id AS id,
               portfolio_id,
               program_name AS name,
               executive_sponsor AS sponsor_name,
               program_lead AS owner_name,
               current_status, current_phase, percent_complete,
               current_milestone_name AS next_milestone_name,
               current_milestone_date AS next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count,
               portfolio_name AS portfolio_name,
               priority,
               planned_start_date,
               planned_end_date,
               delivery_health,
               tech_health,
               team_health,
               last_submitted_update_id,
               created_at,
               updated_at
        FROM app.v_program_current_snapshot
        WHERE portfolio_id = :portfolio_id
          AND COALESCE(is_active, TRUE)
        ORDER BY program_name
        """,
        {"portfolio_id": portfolio_id},
    )
