from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.db.models import FailureEvent
from app.schemas.analytics import (
    CategoryCount,
    CorrelationEntry,
    HeatmapCell,
    OverviewStats,
    ServiceCount,
    TrendPoint,
)


def _default_range(from_time: datetime | None, to_time: datetime | None) -> tuple[datetime, datetime]:
    end = to_time or datetime.now(timezone.utc)
    start = from_time or (end - timedelta(hours=24))
    return start, end


def get_overview(db: Session, from_time: datetime | None = None, to_time: datetime | None = None) -> OverviewStats:
    start, end = _default_range(from_time, to_time)
    period = end - start
    prior_start = start - period

    current = (
        db.query(func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .scalar()
        or 0
    )
    prior = (
        db.query(func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= prior_start, FailureEvent.timestamp < start)
        .scalar()
        or 0
    )

    hours = max(period.total_seconds() / 3600, 0.01)
    delta = ((current - prior) / prior * 100) if prior else (100.0 if current else 0.0)

    return OverviewStats(
        total_failures=current,
        failures_per_hour=round(current / hours, 2),
        delta_percent=round(delta, 2),
        period_hours=round(hours, 2),
    )


def get_trends(
    db: Session,
    interval: str = "hour",
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[TrendPoint]:
    start, end = _default_range(from_time, to_time)
    trunc = "hour" if interval == "hour" else "day"
    bucket = func.date_trunc(trunc, FailureEvent.timestamp).label("bucket")

    rows = (
        db.query(bucket, func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .group_by(bucket)
        .order_by(bucket)
        .all()
    )
    return [TrendPoint(bucket=row[0], count=row[1]) for row in rows]


def get_top_services(
    db: Session,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    limit: int = 10,
) -> list[ServiceCount]:
    start, end = _default_range(from_time, to_time)
    rows = (
        db.query(FailureEvent.service_name, func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .group_by(FailureEvent.service_name)
        .order_by(func.count(FailureEvent.id).desc())
        .limit(limit)
        .all()
    )
    return [ServiceCount(service_name=row[0], count=row[1]) for row in rows]


def get_categories(
    db: Session,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[CategoryCount]:
    start, end = _default_range(from_time, to_time)
    rows = (
        db.query(FailureEvent.error_category, func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .group_by(FailureEvent.error_category)
        .order_by(func.count(FailureEvent.id).desc())
        .all()
    )
    return [CategoryCount(category=row[0], count=row[1]) for row in rows]


def get_heatmap(
    db: Session,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> list[HeatmapCell]:
    start, end = _default_range(from_time, to_time)
    hour_expr = func.extract("hour", FailureEvent.timestamp).label("hour")
    rows = (
        db.query(FailureEvent.service_name, hour_expr, func.count(FailureEvent.id))
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .group_by(FailureEvent.service_name, hour_expr)
        .all()
    )
    return [HeatmapCell(service_name=row[0], hour=int(row[1]), count=row[2]) for row in rows]


def get_correlation(
    db: Session,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    window_minutes: int = 5,
) -> list[CorrelationEntry]:
    start, end = _default_range(from_time, to_time)
    failures = (
        db.query(FailureEvent)
        .filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
        .order_by(FailureEvent.timestamp)
        .all()
    )

    if not failures:
        return []

    window = timedelta(minutes=window_minutes)
    groups: list[list[FailureEvent]] = []
    current_group: list[FailureEvent] = [failures[0]]

    for failure in failures[1:]:
        if failure.timestamp - current_group[-1].timestamp <= window:
            current_group.append(failure)
        else:
            groups.append(current_group)
            current_group = [failure]
    groups.append(current_group)

    results: list[CorrelationEntry] = []
    for group in groups:
        services = sorted({f.service_name for f in group})
        if len(services) < 2:
            continue
        categories = {f.error_category for f in group}
        category = categories.pop() if len(categories) == 1 else "mixed"
        results.append(
            CorrelationEntry(
                services=services,
                category=category,
                count=len(group),
                window_start=group[0].timestamp,
                window_end=group[-1].timestamp,
            )
        )
    return sorted(results, key=lambda x: x.count, reverse=True)
