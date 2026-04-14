from __future__ import annotations

from app.integrations.ado.sync import sync_project_work_items


def run_sync(project_name: str) -> dict[str, int | str]:
    return sync_project_work_items(project_name)
