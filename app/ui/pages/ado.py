from __future__ import annotations

import pandas as pd
import streamlit as st

from app.core.config import load_config
from app.integrations.ado.auth import PatCredentialProvider
from app.integrations.ado.client import AdoClient
from app.services.ado_summary import build_team_scoped_wiql, summarize_counts_by_iteration
from app.ui.exec_reporting_views import render_html
from app.ui.pages.common import ensure_sidebar_state


def _build_client() -> AdoClient:
    cfg = load_config().ado
    return AdoClient(PatCredentialProvider(cfg.pat), cfg.organization)


def render() -> None:
    ensure_sidebar_state(current_page="ADO")
    render_html(
        "<div class='panel-header'><div class='eyebrow'>Integration</div>"
        "<div class='heading'>Azure DevOps</div>"
        "<div class='copy'>Team-scoped work item counts by iteration.</div></div>"
    )

    cfg = load_config().ado
    if not cfg.organization or not cfg.pat:
        st.warning("Missing [azure_devops] secrets. Add organization and pat to query Azure DevOps.")
        st.stop()

    client = _build_client()

    try:
        projects = client.list_projects()
    except Exception as exc:
        st.error(f"Could not load ADO projects: {exc}")
        st.stop()

    project_names = [str(p.get("name", "")).strip() for p in projects if str(p.get("name", "")).strip()]
    if not project_names:
        st.info("No Azure DevOps projects found for this organization.")
        st.stop()

    project = st.selectbox("Project", sorted(project_names), key="ado_project")

    try:
        teams = client.list_teams(project)
    except Exception as exc:
        st.warning(f"Could not load teams for {project}: {exc}")
        teams = []

    team_labels = ["All teams"] + [str(team.get("name", "")).strip() for team in teams if str(team.get("name", "")).strip()]
    selected_team = st.selectbox("Team scope", team_labels, key="ado_team")

    team_area_path: str | None = None
    if selected_team != "All teams":
        team_area_path = f"{project}\\{selected_team}"

    wiql = build_team_scoped_wiql(project=project, area_path=team_area_path)
    with st.expander("WIQL", expanded=False):
        st.code(wiql, language="sql")

    if st.button("Load counts by iteration", type="primary"):
        try:
            ids = client.run_wiql(project, wiql)
        except Exception as exc:
            st.error(f"Failed running WIQL: {exc}")
            st.stop()

        if not ids:
            st.info("No work items found for this project/team scope.")
            return

        items: list[dict[str, object]] = []
        fields = ["System.IterationPath"]
        for start in range(0, len(ids), 200):
            chunk = ids[start : start + 200]
            items.extend(client.get_work_items_batch(project, chunk, fields))

        summary = summarize_counts_by_iteration(items)
        table = pd.DataFrame(summary, columns=["Iteration", "Count"])
        st.metric("Total Work Items", int(table["Count"].sum()))
        st.dataframe(table, use_container_width=True, hide_index=True)
