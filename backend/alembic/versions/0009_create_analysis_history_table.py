"""create analysis_history table

Revision ID: 0009
Revises: 0008
Create Date: 2026-05-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.create_table(
		"analysis_history",
		sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("source_type", sa.String(50), nullable=False),
		sa.Column("source_name", sa.String(255), nullable=True),
		sa.Column("input_text", sa.Text(), nullable=True),
		sa.Column("upload_id", sa.Integer(), nullable=True),
		sa.Column("job_id", sa.String(255), nullable=True, unique=True),
		sa.Column("status", sa.String(50), nullable=False, server_default="completed"),
		sa.Column("include_scores", sa.Boolean(), nullable=False, server_default=sa.text("true")),
		sa.Column("apply_postprocess", sa.Boolean(), nullable=False, server_default=sa.text("true")),
		sa.Column("include_meta", sa.Boolean(), nullable=False, server_default=sa.text("false")),
		sa.Column("item_count", sa.Integer(), nullable=True),
		sa.Column("result_label", sa.String(50), nullable=True),
		sa.Column("result_score", sa.Float(), nullable=True),
		sa.Column("label_counts", sa.JSON(), nullable=True),
		sa.Column("result_payload", sa.JSON(), nullable=True),
		sa.Column("error", sa.Text(), nullable=True),
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
		sa.ForeignKeyConstraint(["upload_id"], ["uploads.id"], ondelete="SET NULL"),
	)
	op.create_index("ix_analysis_history_user_id_created_at", "analysis_history", ["user_id", "created_at"])
	op.create_index("ix_analysis_history_job_id", "analysis_history", ["job_id"])


def downgrade() -> None:
	op.drop_index("ix_analysis_history_job_id", table_name="analysis_history")
	op.drop_index("ix_analysis_history_user_id_created_at", table_name="analysis_history")
	op.drop_table("analysis_history")