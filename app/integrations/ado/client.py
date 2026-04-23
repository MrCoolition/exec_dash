from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import load_config
from app.integrations.ado.auth import AdoCredentialProvider
from app.integrations.ado.endpoints import base_url, normalize_organization


class AdoClient:
    def __init__(self, creds: AdoCredentialProvider, organization: str | None = None) -> None:
        cfg = load_config().ado
        self.organization = normalize_organization(organization or cfg.organization)
        self.api_version = cfg.api_version
        self.headers = creds.get_auth_headers()
        self.base = base_url(self.organization)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def _get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        with httpx.Client(timeout=20) as client:
            response = client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

    def list_projects(self) -> list[dict[str, Any]]:
        payload = self._get(f"{self.base}/_apis/projects", {"api-version": self.api_version})
        return payload.get("value", [])

    def list_teams(self, project: str) -> list[dict[str, Any]]:
        payload = self._get(f"{self.base}/_apis/projects/{project}/teams", {"api-version": self.api_version})
        return payload.get("value", [])

    def list_queries(self, project: str) -> dict[str, Any]:
        return self._get(f"{self.base}/{project}/_apis/wit/queries", {"api-version": self.api_version})

    def run_saved_query(self, project: str, query_id: str) -> list[int]:
        payload = self._get(
            f"{self.base}/{project}/_apis/wit/wiql/{query_id}",
            {"api-version": self.api_version},
        )
        return [item["id"] for item in payload.get("workItems", [])]

    def run_wiql(self, project: str, wiql: str) -> list[int]:
        url = f"{self.base}/{project}/_apis/wit/wiql?api-version={self.api_version}"
        with httpx.Client(timeout=20) as client:
            resp = client.post(url, headers={**self.headers, "Content-Type": "application/json"}, json={"query": wiql})
            resp.raise_for_status()
            data = resp.json()
        return [item["id"] for item in data.get("workItems", [])]

    def get_work_items_batch(self, project: str, ids: list[int], fields: list[str]) -> list[dict[str, Any]]:
        url = f"{self.base}/{project}/_apis/wit/workitemsbatch?api-version={self.api_version}"
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                url,
                headers={**self.headers, "Content-Type": "application/json"},
                json={"ids": ids, "fields": fields},
            )
            resp.raise_for_status()
            data = resp.json()
        return data.get("value", [])

    def list_iterations(self, project: str, team: str) -> dict[str, Any]:
        return self._get(
            f"{self.base}/{project}/{team}/_apis/work/teamsettings/iterations",
            {"api-version": self.api_version},
        )

    def list_builds(self, project: str) -> dict[str, Any]:
        return self._get(f"{self.base}/{project}/_apis/build/builds", {"api-version": self.api_version})

    def list_pipeline_runs(self, project: str) -> dict[str, Any]:
        return self._get(f"{self.base}/{project}/_apis/pipelines/runs", {"api-version": self.api_version})

    def list_releases(self, project: str) -> dict[str, Any]:
        return self._get(f"https://vsrm.dev.azure.com/{self.organization}/{project}/_apis/release/releases", {"api-version": self.api_version})
