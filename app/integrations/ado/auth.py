from __future__ import annotations

import base64
from abc import ABC, abstractmethod


class AdoCredentialProvider(ABC):
    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        raise NotImplementedError


class PatCredentialProvider(AdoCredentialProvider):
    def __init__(self, pat: str) -> None:
        self._pat = pat

    def get_auth_headers(self) -> dict[str, str]:
        token = base64.b64encode(f":{self._pat}".encode("utf-8")).decode("utf-8")
        return {"Authorization": f"Basic {token}"}
