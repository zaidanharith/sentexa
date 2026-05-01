"""create uploads, sentiment_jobs, sentiment_job_results, reports, feedback, alerts tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-01

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"uploads",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("filename", sa.String(255), nullable=False),
		sa.Column("file_type", sa.String(50), nullable=False),
		sa.Column("file_path", sa.String(255), nullable=False),
		sa.Column("rows_count", sa.Integer(), nullable=False),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column("status", sa.String(50), nullable=False, server_default="uploaded"),
		sa.Column("error", sa.Text(), nullable=True),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
	)

	op.create_table(
		"sentiment_jobs",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("job_id", sa.String(255), nullable=False, unique=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("status", sa.String(50), nullable=False, server_default="queued"),
		sa.Column("total_texts", sa.Integer(), nullable=False),
		sa.Column("completed_count", sa.Integer(), nullable=False, server_default="0"),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column(
			"updated_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column("label_counts", sa.JSON(), nullable=True),
		sa.Column("error", sa.Text(), nullable=True),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
	)

	op.create_table(
		"sentiment_job_results",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("job_id", sa.String(255), nullable=False),
		sa.Column("index", sa.Integer(), nullable=False),
		sa.Column("text", sa.Text(), nullable=False),
		sa.Column("label", sa.String(50), nullable=False),
		sa.Column("label_id", sa.Integer(), nullable=True),
		sa.Column("score", sa.Float(), nullable=True),
		sa.Column("scores", sa.JSON(), nullable=True),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.ForeignKeyConstraint(["job_id"], ["sentiment_jobs.job_id"], ondelete="CASCADE"),
	)

	op.create_table(
		"reports",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("title", sa.String(255), nullable=False),
		sa.Column("description", sa.Text(), nullable=True),
		sa.Column("job_id", sa.String(255), nullable=True),
		sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
		sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
		sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
		sa.Column("format", sa.String(50), nullable=False, server_default="csv"),
		sa.Column("file_path", sa.String(255), nullable=True),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column(
			"updated_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
	)

	op.create_table(
		"feedback",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("job_id", sa.String(255), nullable=True),
		sa.Column("text", sa.Text(), nullable=False),
		sa.Column("original_label", sa.String(50), nullable=False),
		sa.Column("corrected_label", sa.String(50), nullable=False),
		sa.Column("reason", sa.Text(), nullable=True),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
	)

	op.create_table(
		"alerts",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("job_id", sa.String(255), nullable=True),
		sa.Column("text", sa.Text(), nullable=False),
		sa.Column("label", sa.String(50), nullable=False),
		sa.Column("severity", sa.String(50), nullable=False, server_default="medium"),
		sa.Column("reason", sa.Text(), nullable=True),
		sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
		sa.Column(
			"created_at",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
		sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
	)


def downgrade() -> None:
	op.drop_table("alerts")
	op.drop_table("feedback")
	op.drop_table("reports")
	op.drop_table("sentiment_job_results")
	op.drop_table("sentiment_jobs")
	op.drop_table("uploads")
