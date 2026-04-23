from __future__ import annotations

from collections import Counter


def build_team_scoped_wiql(project: str, area_path: str | None = None) -> str:
    """Build a WIQL query optionally scoped to a team's area path."""
    escaped_project = project.replace("'", "''")
    clauses = [f"[System.TeamProject] = '{escaped_project}'"]
    if area_path:
        escaped_area = area_path.replace("'", "''")
        clauses.append(f"[System.AreaPath] UNDER '{escaped_area}'")

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
