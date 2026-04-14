from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass
class User:
    provider: str
    provider_sub: str
    email: str | None = None
    display_name: str | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class WeeklyUpdate:
    tenant_id: UUID
    ado_project_id: UUID | None = None
    week_ending: date | None = None
    executive_summary: str | None = None
    accomplishments: str | None = None
    next_steps: str | None = None
    dependencies: str | None = None
    updated_at: datetime | None = None
