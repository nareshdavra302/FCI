from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_failures: int
    failures_per_hour: float
    delta_percent: float
    period_hours: float


class TrendPoint(BaseModel):
    bucket: datetime
    count: int


class ServiceCount(BaseModel):
    service_name: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class HeatmapCell(BaseModel):
    service_name: str
    hour: int
    count: int


class CorrelationEntry(BaseModel):
    services: list[str]
    category: str
    count: int
    window_start: datetime
    window_end: datetime
