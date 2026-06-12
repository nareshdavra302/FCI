from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import ErrorCategory, FailureEvent
from app.schemas.failure import FailureIngestRequest, FailureResponse
from app.services.categorization import categorize_error


def ingest_failure(db: Session, payload: FailureIngestRequest) -> FailureResponse:
    category = categorize_error(payload.error_message, payload.stack_trace)
    event = FailureEvent(
        service_name=payload.service_name,
        endpoint=payload.endpoint,
        method=payload.method.upper(),
        status_code=payload.status_code,
        error_message=payload.error_message,
        stack_trace=payload.stack_trace,
        error_category=ErrorCategory(category.value),
        request_metadata=payload.request_metadata,
        timestamp=payload.timestamp or datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return FailureResponse.model_validate(event)


def ingest_failures_batch(db: Session, payloads: list[FailureIngestRequest]) -> list[FailureResponse]:
    results = []
    for payload in payloads:
        results.append(ingest_failure(db, payload))
    return results


def get_failure_by_id(db: Session, failure_id: UUID) -> FailureEvent | None:
    return db.query(FailureEvent).filter(FailureEvent.id == failure_id).first()


def list_failures(
    db: Session,
    *,
    service: str | None = None,
    category: str | None = None,
    search: str | None = None,
    incident_group_id: UUID | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[FailureEvent], int]:
    query = db.query(FailureEvent)

    if service:
        query = query.filter(FailureEvent.service_name == service)
    if category:
        query = query.filter(FailureEvent.error_category == ErrorCategory(category))
    if incident_group_id:
        query = query.filter(FailureEvent.incident_group_id == incident_group_id)
    if from_time:
        query = query.filter(FailureEvent.timestamp >= from_time)
    if to_time:
        query = query.filter(FailureEvent.timestamp <= to_time)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (FailureEvent.error_message.ilike(pattern))
            | (FailureEvent.endpoint.ilike(pattern))
            | (FailureEvent.service_name.ilike(pattern))
        )

    total = query.count()
    items = (
        query.order_by(FailureEvent.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total
