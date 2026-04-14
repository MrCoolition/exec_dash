from app.integrations.ado.mappers import map_work_item


def test_map_work_item():
    out = map_work_item({"id": 1, "fields": {"System.Title": "A", "System.State": "Active"}})
    assert out["work_item_id"] == 1
    assert out["state"] == "Active"
