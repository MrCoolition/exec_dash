from __future__ import annotations

from app.db import fetch_all, fetch_one


def list_portfolios() -> list[dict]:
    return fetch_all(
        """
        SELECT portfolio_id AS id,
               portfolio_name AS name,
               NULL::text AS owner_name,
               NULL::text AS description
        FROM app.portfolio
        WHERE is_active = TRUE
        ORDER BY sort_order, portfolio_name
        """
    )


def get_portfolio_by_program(program_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT p.portfolio_id AS id,
               p.portfolio_name AS name,
               NULL::text AS owner_name,
               NULL::text AS description
        FROM app.portfolio p
        JOIN app.program pr ON pr.portfolio_id = p.portfolio_id
        WHERE pr.program_id = :program_id
        """,
        {"program_id": program_id},
    )


def get_portfolio(portfolio_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT portfolio_id AS id,
               portfolio_name AS name,
               NULL::text AS owner_name,
               NULL::text AS description
        FROM app.portfolio
        WHERE portfolio_id = :portfolio_id
        """,
        {"portfolio_id": portfolio_id},
    )
