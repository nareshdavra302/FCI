from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.failure import FailureResponse, PaginatedFailures
from app.services.ingestion import get_failure_by_id, list_failures


router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("", response_model=PaginatedFailures)
def get_incidents(
    service: str | None = None,
    category: str | None = None,
    search: str | None = None,
    incident_group_id: UUID | None = None,
    from_time: datetime | None = Query(None, alias="from"),
    to_time: datetime | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = list_failures(
        db,
        service=service,
        category=category,
        search=search,
        incident_group_id=incident_group_id,
        from_time=from_time,
        to_time=to_time,
        page=page,
        page_size=page_size,
    )
    return PaginatedFailures(
        items=[FailureResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{incident_id}", response_model=FailureResponse)
def get_incident(incident_id: UUID, db: Session = Depends(get_db)):
    failure = get_failure_by_id(db, incident_id)
    if not failure:
        raise HTTPException(status_code=404, detail="Incident not found")
    return FailureResponse.model_validate(failure)
