from __future__ import annotations


def map_work_item(raw: dict) -> dict:
    fields = raw.get("fields", {})
    return {
        "work_item_id": raw.get("id"),
        "title": fields.get("System.Title"),
        "state": fields.get("System.State"),
        "target_date": fields.get("Microsoft.VSTS.Scheduling.TargetDate"),
        "raw_fields": fields,
    }
