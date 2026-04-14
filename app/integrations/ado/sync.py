from __future__ import annotations

from app.core.config import load_config
from app.integrations.ado.auth import PatCredentialProvider
from app.integrations.ado.client import AdoClient
from app.integrations.ado.mappers import map_work_item


def sync_project_work_items(project_name: str) -> dict[str, int | str]:
    cfg = load_config().ado
    client = AdoClient(PatCredentialProvider(cfg.pat), cfg.organization)
    ids = client.run_wiql(project_name, "Select [System.Id] From WorkItems Where [System.TeamProject] = @project")
    processed = 0
    for start in range(0, len(ids), 200):
        chunk = ids[start : start + 200]
        items = client.get_work_items_batch(project_name, chunk, ["System.Title", "System.State"])
        _ = [map_work_item(i) for i in items]
        processed += len(items)
    return {"project": project_name, "processed": processed}
