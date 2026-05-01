"""update sentiment_job_results to reference sentiment_jobs id instead of job_id

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.drop_constraint(
		"sentiment_job_results_job_id_fkey",
		"sentiment_job_results",
		type_="foreignkey"
	)
	
	op.execute(
		"ALTER TABLE sentiment_job_results ALTER COLUMN job_id TYPE INTEGER USING job_id::integer"
	)
	
	op.create_foreign_key(
		"sentiment_job_results_job_id_fkey",
		"sentiment_job_results",
		"sentiment_jobs",
		["job_id"],
		["id"],
		ondelete="CASCADE",
	)


def downgrade() -> None:
	op.drop_constraint(
		"sentiment_job_results_job_id_fkey",
		"sentiment_job_results",
		type_="foreignkey"
	)
	
	op.execute(
		"ALTER TABLE sentiment_job_results ALTER COLUMN job_id TYPE VARCHAR(255) USING job_id::text"
	)
	
	op.create_foreign_key(
		"sentiment_job_results_job_id_fkey",
		"sentiment_job_results",
		"sentiment_jobs",
		["job_id"],
		["job_id"],
		ondelete="CASCADE",
	)
