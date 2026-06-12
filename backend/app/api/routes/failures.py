from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.failure import FailureBatchRequest, FailureIngestRequest, FailureResponse, PaginatedFailures
from app.services.ingestion import get_failure_by_id, ingest_failure, ingest_failures_batch, list_failures

router = APIRouter(prefix="/failures", tags=["failures"])


@router.post("", response_model=FailureResponse, status_code=201)
def create_failure(payload: FailureIngestRequest, db: Session = Depends(get_db)):
    return ingest_failure(db, payload)


@router.post("/batch", response_model=list[FailureResponse], status_code=201)
def create_failures_batch(payload: FailureBatchRequest, db: Session = Depends(get_db)):
    return ingest_failures_batch(db, payload.failures)


