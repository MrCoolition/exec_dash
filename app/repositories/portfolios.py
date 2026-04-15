from __future__ import annotations

from app.db import fetch_all, fetch_one


def list_portfolios() -> list[dict]:
    return fetch_all(
        """
        SELECT id, name, owner_name, description
        FROM portfolio
        ORDER BY name
        """
    )


def get_portfolio_by_program(program_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT p.id, p.name, p.owner_name, p.description
        FROM portfolio p
        JOIN program pr ON pr.portfolio_id = p.id
        WHERE pr.id = :program_id
        """,
        {"program_id": program_id},
    )
