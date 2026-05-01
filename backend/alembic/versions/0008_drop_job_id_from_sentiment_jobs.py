"""drop job_id column from sentiment_jobs

Revision ID: 0008
Revises: 0007
Create Date: 2026-05-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.drop_column("sentiment_jobs", "job_id")


def downgrade() -> None:
	op.add_column(
		"sentiment_jobs",
		sa.Column("job_id", sa.String(255), nullable=False),
	)
	op.create_unique_constraint(
		"uq_sentiment_jobs_job_id",
		"sentiment_jobs",
		["job_id"],
	)
