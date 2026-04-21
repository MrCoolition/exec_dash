from __future__ import annotations

from app.repositories.programs import get_program
from app.services.exec_reporting_adapter import build_exec_dataframe
from app.ui.exec_reporting_views import render_html, render_program_one_pager
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    state = ensure_sidebar_state(current_page="Program One-Pager")
    program = get_program(state["selected_program_id"])
    if not program:
        render_html("<div class='dash-card'><div class='copy'>Selected program not found.</div></div>")
        return

    df = build_exec_dataframe([program])
    program_name = df.iloc[0]["Program"]
    portfolio_name = df.iloc[0].get("portfolio_name") or state["selected_portfolio"]["name"]

    render_program_one_pager(
        portfolio=portfolio_name,
        program=program_name,
        df=df,
        reporting_date=state["reporting_date"],
    )
