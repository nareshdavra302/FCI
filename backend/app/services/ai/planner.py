import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import FailureEvent


@dataclass
class IncidentGroup:
    group_id: uuid.UUID
    failures: list[FailureEvent] = field(default_factory=list)

    @property
    def service_names(self) -> set[str]:
        return {f.service_name for f in self.failures}

    @property
    def categories(self) -> set[str]:
        return {f.error_category.value for f in self.failures}

    @property
    def first_seen(self) -> datetime | None:
        return min((f.timestamp for f in self.failures), default=None)

    @property
    def last_seen(self) -> datetime | None:
        return max((f.timestamp for f in self.failures), default=None)


def _endpoint_prefix(endpoint: str) -> str:
    parts = endpoint.strip("/").split("/")
    if len(parts) >= 2:
        return f"/{parts[0]}/{parts[1]}"
    return endpoint


def cluster_failures(
    db: Session,
    failures: list[FailureEvent],
    window_minutes: int | None = None,
) -> list[IncidentGroup]:
    if not failures:
        return []

    settings = get_settings()
    window = timedelta(minutes=window_minutes or settings.planner_window_minutes)
    sorted_failures = sorted(failures, key=lambda f: f.timestamp)

    groups: list[IncidentGroup] = []
    current_key: tuple | None = None
    current_group: IncidentGroup | None = None

    for failure in sorted_failures:
        key = (
            failure.service_name,
            failure.error_category.value,
            _endpoint_prefix(failure.endpoint),
        )
        if (
            current_group is None
            or key != current_key
            or failure.timestamp - current_group.last_seen > window
        ):
            current_group = IncidentGroup(group_id=uuid.uuid4(), failures=[failure])
            groups.append(current_group)
            current_key = key
        else:
            current_group.failures.append(failure)

    for group in groups:
        for failure in group.failures:
            failure.incident_group_id = group.group_id
    db.commit()
    return groups


def compute_signals(group: IncidentGroup) -> dict:
    duration_minutes = 0.0
    if group.first_seen and group.last_seen:
        duration_minutes = max((group.last_seen - group.first_seen).total_seconds() / 60, 0.01)

    return {
        "failure_count": len(group.failures),
        "affected_services": sorted(group.service_names),
        "categories": sorted(group.categories),
        "burst_rate_per_minute": round(len(group.failures) / duration_minutes, 2),
        "first_seen": group.first_seen.isoformat() if group.first_seen else None,
        "last_seen": group.last_seen.isoformat() if group.last_seen else None,
        "endpoints": sorted({f.endpoint for f in group.failures}),
    }
