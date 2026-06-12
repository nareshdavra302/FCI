from typing import Literal

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import CategoryCount, CorrelationEntry, HeatmapCell, OverviewStats, ServiceCount, TrendPoint
from app.services.analytics import (
    get_categories,
    get_correlation,
    get_heatmap,
    get_overview,
    get_top_services,
    get_trends,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewStats)
def analytics_overview(
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    return get_overview(db, from_time, to_time)


@router.get("/trends", response_model=list[TrendPoint])
def analytics_trends(
    interval: Literal["hour", "day"] = Query("hour"),
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    return get_trends(db, interval, from_time, to_time)


@router.get("/services", response_model=list[ServiceCount])
def analytics_services(
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return get_top_services(db, from_time, to_time, limit)


@router.get("/categories", response_model=list[CategoryCount])
def analytics_categories(
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    return get_categories(db, from_time, to_time)


@router.get("/heatmap", response_model=list[HeatmapCell])
def analytics_heatmap(
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    return get_heatmap(db, from_time, to_time)


@router.get("/correlation", response_model=list[CorrelationEntry])
def analytics_correlation(
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    window_minutes: int = Query(5, ge=1, le=60),
    db: Session = Depends(get_db),
):
    return get_correlation(db, from_time, to_time, window_minutes)
