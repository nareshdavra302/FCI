import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ErrorCategory(str, enum.Enum):
    database = "database"
    timeout = "timeout"
    dependency = "dependency"
    authentication = "authentication"
    configuration = "configuration"
    unknown = "unknown"


class GeneratedBy(str, enum.Enum):
    rule_engine = "rule_engine"
    llm = "llm"
    hybrid = "hybrid"


class FailureEvent(Base):
    __tablename__ = "failure_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(128), index=True)
    endpoint: Mapped[str] = mapped_column(String(512))
    method: Mapped[str] = mapped_column(String(16))
    status_code: Mapped[int] = mapped_column(Integer, default=500)
    error_message: Mapped[str] = mapped_column(Text)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_category: Mapped[str] = mapped_column(String(128), index=True)
    request_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    incident_group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class InsightReport(Base):
    __tablename__ = "insight_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_group_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text)
    root_cause_hypotheses: Mapped[list] = mapped_column(JSONB)
    recommendations: Mapped[list] = mapped_column(JSONB)
    risk_level: Mapped[str] = mapped_column(String(32))
    remediation_steps: Mapped[list] = mapped_column(JSONB)
    operational_signals: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_by: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
