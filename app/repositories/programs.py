from __future__ import annotations

from app.db import fetch_all, fetch_one


def list_programs() -> list[dict]:
    return fetch_all(
        """
        SELECT id, portfolio_id, name, sponsor_name, owner_name,
               current_status, current_phase, percent_complete,
               next_milestone_name, next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count
        FROM program
        ORDER BY name
        """
    )


def get_program(program_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT id, portfolio_id, name, sponsor_name, owner_name,
               current_status, current_phase, percent_complete,
               next_milestone_name, next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count
        FROM program
        WHERE id = :program_id
        """,
        {"program_id": program_id},
    )


def list_program_snapshots_by_portfolio(portfolio_id: str) -> list[dict]:
    return fetch_all(
        """
        SELECT id, portfolio_id, name, sponsor_name, owner_name,
               current_status, current_phase, percent_complete,
               next_milestone_name, next_milestone_date,
               summary, upcoming_work, risk_detail, mitigation,
               decision_needed, status_note, next_step,
               open_risks_count, escalations_count
        FROM program
        WHERE portfolio_id = :portfolio_id
        ORDER BY name
        """,
        {"portfolio_id": portfolio_id},
    )
