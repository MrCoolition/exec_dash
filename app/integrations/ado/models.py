from __future__ import annotations

from pydantic import BaseModel


class AdoWorkItem(BaseModel):
    id: int
    fields: dict
