"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # error_category = postgresql.ENUM(
    #     "database", "timeout", "dependency", "authentication", "configuration", "unknown",
    #     name="errorcategory",
    # )
    # generated_by = postgresql.ENUM("rule_engine", "llm", "hybrid", name="generatedby")
    # error_category.create(op.get_bind(), checkfirst=True)
    # generated_by.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "failure_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("service_name", sa.String(128), nullable=False),
        sa.Column("endpoint", sa.String(512), nullable=False),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("error_category", sa.String(255), nullable=False),
        sa.Column("request_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("incident_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_failure_events_service_name", "failure_events", ["service_name"])
    op.create_index("ix_failure_events_error_category", "failure_events", ["error_category"])
    op.create_index("ix_failure_events_timestamp", "failure_events", ["timestamp"])
    op.create_index("ix_failure_events_incident_group_id", "failure_events", ["incident_group_id"])

    op.create_table(
        "insight_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("root_cause_hypotheses", postgresql.JSONB(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(), nullable=False),
        sa.Column("risk_level", sa.String(32), nullable=False),
        sa.Column("remediation_steps", postgresql.JSONB(), nullable=False),
        sa.Column("operational_signals", postgresql.JSONB(), nullable=True),
        sa.Column("generated_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_insight_reports_incident_group_id", "insight_reports", ["incident_group_id"], unique=True)


def downgrade() -> None:
    op.drop_table("insight_reports")
    op.drop_table("failure_events")
    # op.execute("DROP TYPE IF EXISTS generatedby")
    # op.execute("DROP TYPE IF EXISTS errorcategory")
