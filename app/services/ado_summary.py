from __future__ import annotations

from collections import Counter


def _escape_wiql_literal(value: str) -> str:
    return value.replace("'", "''")


def build_team_scoped_wiql(
    project: str,
    area_path: str | None = None,
    team_area_paths: list[tuple[str, bool]] | None = None,
) -> str:
    """Build a WIQL query optionally scoped to a team's area path."""
    escaped_project = _escape_wiql_literal(project)
    clauses = [f"[System.TeamProject] = '{escaped_project}'"]

    area_clauses: list[str] = []
    if team_area_paths:
        for path, include_children in team_area_paths:
            escaped_area = _escape_wiql_literal(path)
            operator = "UNDER" if include_children else "="
            area_clauses.append(f"[System.AreaPath] {operator} '{escaped_area}'")
    elif area_path:
        escaped_area = _escape_wiql_literal(area_path)
        area_clauses.append(f"[System.AreaPath] UNDER '{escaped_area}'")

    if area_clauses:
        clauses.append(f"({' OR '.join(area_clauses)})")

    where_clause = " AND ".join(clauses)
    return (
        "SELECT [System.Id], [System.IterationPath] FROM WorkItems "
        f"WHERE {where_clause} "
        "ORDER BY [System.ChangedDate] DESC"
    )


def summarize_counts_by_iteration(work_items: list[dict[str, object]]) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    for item in work_items:
        fields = item.get("fields")
        if not isinstance(fields, dict):
            continue
        iteration = str(fields.get("System.IterationPath") or "Unassigned").strip() or "Unassigned"
        counts[iteration] += 1

    return sorted(counts.items(), key=lambda entry: (-entry[1], entry[0].lower()))
