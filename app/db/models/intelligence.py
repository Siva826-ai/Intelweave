import uuid
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, now

class Entity(Base):
    __tablename__ = "entities"
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    risk_score: Mapped[float] = mapped_column(Numeric(5,2), nullable=False, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5,2), nullable=False, default=0.0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, nullable=False)

class Insight(Base):
    __tablename__ = "insights"
    insight_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.case_id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="low")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Numeric(5,2), nullable=False, default=0.0)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, nullable=False)

class Relationship(Base):
    __tablename__ = "relationships"
    rel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cases.case_id"), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.entity_id"), nullable=False)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("entities.entity_id"), nullable=False)
    basis: Mapped[str] = mapped_column(String(255), nullable=False)
    strength_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now, nullable=False)
