"""add ai analysis fields to reviews table

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.add_column("reviews", sa.Column("ai_scores", sa.JSON(), nullable=True))
	op.add_column(
		"reviews",
		sa.Column("ai_processed_at", sa.DateTime(timezone=True), nullable=True),
	)
	op.add_column("reviews", sa.Column("ai_postprocess_meta", sa.JSON(), nullable=True))
	op.add_column("reviews", sa.Column("analysis_source", sa.String(50), nullable=True))
	op.add_column("reviews", sa.Column("job_id", sa.String(255), nullable=True))


def downgrade() -> None:
	op.drop_column("reviews", "job_id")
	op.drop_column("reviews", "analysis_source")
	op.drop_column("reviews", "ai_postprocess_meta")
	op.drop_column("reviews", "ai_processed_at")
	op.drop_column("reviews", "ai_scores")
