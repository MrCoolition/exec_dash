from app.services.rollups import overview_rollup


def test_overview_rollup():
    result = overview_rollup([
        {"state": "Done", "is_overdue": False},
        {"state": "Active", "is_overdue": True},
    ])
    assert result["total"] == 2
    assert result["overdue"] == 1
