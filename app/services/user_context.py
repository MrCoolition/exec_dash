from __future__ import annotations

from dataclasses import dataclass

from app.models.pydantic_models import User


@dataclass(frozen=True)
class UserContext:
    user: User
    role_codes: set[str]
    tenant_slugs: list[str]
