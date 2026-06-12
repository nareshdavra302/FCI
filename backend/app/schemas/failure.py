from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ErrorCategoryEnum(str, Enum):
    database = "database"
    timeout = "timeout"
    dependency = "dependency"
    authentication = "authentication"
    configuration = "configuration"
    unknown = "unknown"


class FailureIngestRequest(BaseModel):
    service_name: str
    endpoint: str
    method: str
    status_code: int = 500
    error_message: str
    stack_trace: str | None = None
    request_metadata: dict | None = None
    timestamp: datetime | None = None


class FailureResponse(BaseModel):
    id: UUID
    service_name: str
    endpoint: str
    method: str
    status_code: int
    error_message: str
    stack_trace: str | None
    error_category: ErrorCategoryEnum
    request_metadata: dict | None
    timestamp: datetime
    incident_group_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FailureBatchRequest(BaseModel):
    failures: list[FailureIngestRequest]


class PaginatedFailures(BaseModel):
    items: list[FailureResponse]
    total: int
    page: int
    page_size: int
