from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from app.repositories.programs import list_program_snapshots_by_portfolio
from app.services.exec_reporting_adapter import build_exec_dataframe
from app.ui.exec_reporting_views import render_dashboard, render_html
from app.ui.pages.common import ensure_sidebar_state

APP_TIMEZONE = ZoneInfo("America/New_York")


def render() -> None:
    state = ensure_sidebar_state(current_page="Impower Portfolio")
    portfolio = state.get("selected_portfolio")
    if not portfolio:
        render_html("<div class='dash-card'><div class='copy'>No portfolio selected. Choose a program from the sidebar.</div></div>")
        return

    rows = list_program_snapshots_by_portfolio(str(portfolio["id"]))
    df = build_exec_dataframe(rows)
    render_dashboard(
        portfolio_name=portfolio.get("name") or "FY25 Strategic Program Intelligence",
        df=df,
        reporting_date=state["reporting_date"],
        refreshed_at=datetime.now(APP_TIMEZONE),
        current_user=state.get("current_user"),
    )
