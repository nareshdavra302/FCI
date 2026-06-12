from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class GeneratedByEnum(str, Enum):
    rule_engine = "rule_engine"
    llm = "llm"
    hybrid = "hybrid"


class AnalyzeRequest(BaseModel):
    from_time: datetime | None = None
    to_time: datetime | None = None
    incident_group_id: UUID | None = None


class InsightReportResponse(BaseModel):
    id: UUID
    incident_group_id: UUID
    summary: str
    root_cause_hypotheses: list[str]
    recommendations: list[str]
    risk_level: str
    remediation_steps: list[str]
    operational_signals: dict | None
    generated_by: GeneratedByEnum
    created_at: datetime

    model_config = {"from_attributes": True}
