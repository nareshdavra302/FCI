from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.insight import AnalyzeRequest, InsightReportResponse
from app.services.ai.workflow import get_insight_by_group_id, list_insights, run_analysis

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/analyze", response_model=list[InsightReportResponse])
async def analyze_insights(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    reports = await run_analysis(
        db,
        from_time=payload.from_time,
        to_time=payload.to_time,
        incident_group_id=payload.incident_group_id,
    )
    return [InsightReportResponse.model_validate(r) for r in reports]


@router.get("", response_model=list[InsightReportResponse])
def get_insights(db: Session = Depends(get_db)):
    return [InsightReportResponse.model_validate(r) for r in list_insights(db)]


@router.get("/{group_id}", response_model=InsightReportResponse)
def get_insight(group_id: UUID, db: Session = Depends(get_db)):
    report = get_insight_by_group_id(db, group_id)
    if not report:
        raise HTTPException(status_code=404, detail="Insight report not found")
    return InsightReportResponse.model_validate(report)
