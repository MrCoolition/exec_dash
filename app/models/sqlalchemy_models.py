from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    tenant_type: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String)
    provider_sub: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str | None] = mapped_column(String)
    display_name: Mapped[str | None] = mapped_column(String)
    raw_profile: Mapped[dict] = mapped_column(JSONB, default=dict)


class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    __table_args__ = (UniqueConstraint("user_id", "role_code", "tenant_id", "project_key", "team_key"),)

    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    role_code: Mapped[str] = mapped_column(String)
    tenant_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    project_key: Mapped[str | None] = mapped_column(String, nullable=True)
    team_key: Mapped[str | None] = mapped_column(String, nullable=True)


class WeeklyUpdate(Base):
    __tablename__ = "weekly_updates"
    id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    ado_project_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    week_ending: Mapped[datetime] = mapped_column(Date)
    executive_summary: Mapped[str | None] = mapped_column(Text)
    accomplishments: Mapped[str | None] = mapped_column(Text)
    next_steps: Mapped[str | None] = mapped_column(Text)
    dependencies: Mapped[str | None] = mapped_column(Text)
    status_override: Mapped[str | None] = mapped_column(String)


class WorkItemCurrent(Base):
    __tablename__ = "work_item_current"
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    ado_project_id: Mapped[str] = mapped_column(UUID(as_uuid=True), primary_key=True)
    work_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(String)
    target_date: Mapped[datetime | None] = mapped_column(Date)
    raw_fields: Mapped[dict] = mapped_column(JSONB, default=dict)
