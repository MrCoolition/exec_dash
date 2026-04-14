from app.services.health import freshness_label


def test_freshness_states():
    assert freshness_label(10) == "fresh"
    assert freshness_label(90) == "warning"
    assert freshness_label(600) == "stale"
    assert freshness_label(1500) == "critical stale"
