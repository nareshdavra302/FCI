from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import FailureEvent, GeneratedBy, InsightReport
from app.services.ai.analyzer import analyze_incident_group
from app.services.ai.planner import IncidentGroup, cluster_failures


async def run_analysis(
    db: Session,
    *,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    incident_group_id: UUID | None = None,
) -> list[InsightReport]:
    end = to_time or datetime.now(timezone.utc)
    start = from_time or (end - timedelta(hours=24))

    query = db.query(FailureEvent).filter(FailureEvent.timestamp >= start, FailureEvent.timestamp <= end)
    if incident_group_id:
        query = query.filter(FailureEvent.incident_group_id == incident_group_id)

    failures = query.order_by(FailureEvent.timestamp).all()
    if not failures:
        return []

    if incident_group_id:
        groups = [IncidentGroup(group_id=incident_group_id, failures=failures)]
    else:
        groups = cluster_failures(db, failures)

    reports: list[InsightReport] = []
    for group in groups:
        existing = (
            db.query(InsightReport)
            .filter(InsightReport.incident_group_id == group.group_id)
            .first()
        )
        if existing and not incident_group_id:
            reports.append(existing)
            continue

        report_data, generated_by = await analyze_incident_group(group)
        if existing:
            existing.summary = report_data["summary"]
            existing.root_cause_hypotheses = report_data["root_cause_hypotheses"]
            existing.recommendations = report_data["recommendations"]
            existing.risk_level = report_data["risk_level"]
            existing.remediation_steps = report_data["remediation_steps"]
            existing.operational_signals = report_data["operational_signals"]
            existing.generated_by = GeneratedBy(generated_by)
            db.commit()
            db.refresh(existing)
            reports.append(existing)
        else:
            report = InsightReport(
                incident_group_id=group.group_id,
                summary=report_data["summary"],
                root_cause_hypotheses=report_data["root_cause_hypotheses"],
                recommendations=report_data["recommendations"],
                risk_level=report_data["risk_level"],
                remediation_steps=report_data["remediation_steps"],
                operational_signals=report_data["operational_signals"],
                generated_by=GeneratedBy(generated_by),
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            reports.append(report)

    return reports


def get_insight_by_group_id(db: Session, group_id: UUID) -> InsightReport | None:
    return db.query(InsightReport).filter(InsightReport.incident_group_id == group_id).first()


def list_insights(db: Session, limit: int = 50) -> list[InsightReport]:
    return (
        db.query(InsightReport)
        .order_by(InsightReport.created_at.desc())
        .limit(limit)
        .all()
    )
