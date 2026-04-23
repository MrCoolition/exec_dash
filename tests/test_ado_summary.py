from app.services.ado_summary import build_team_scoped_wiql, summarize_counts_by_iteration


def test_build_team_scoped_wiql_without_team_scope():
    wiql = build_team_scoped_wiql("Platform")
    assert "[System.TeamProject] = 'Platform'" in wiql
    assert "[System.AreaPath] UNDER" not in wiql


def test_build_team_scoped_wiql_with_team_scope_and_escaping():
    wiql = build_team_scoped_wiql("Plat'form", "Plat'form\\Core Team")
    assert "[System.TeamProject] = 'Plat''form'" in wiql
    assert "[System.AreaPath] UNDER 'Plat''form\\Core Team'" in wiql


def test_summarize_counts_by_iteration_groups_and_defaults():
    items = [
        {"fields": {"System.IterationPath": "A\\Sprint 1"}},
        {"fields": {"System.IterationPath": "A\\Sprint 1"}},
        {"fields": {"System.IterationPath": "A\\Sprint 2"}},
        {"fields": {}},
        {},
    ]

    summary = summarize_counts_by_iteration(items)

    assert summary[0] == ("A\\Sprint 1", 2)
    assert ("A\\Sprint 2", 1) in summary
    assert ("Unassigned", 1) in summary
