"""drop reviews table

Revision ID: 0013
Revises: 0012
Create Date: 2026-05-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	# Drop reviews table
	op.drop_table("reviews")


def downgrade() -> None:
	# Recreate reviews table
	op.create_table(
		"reviews",
		sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
		sa.Column("user_id", sa.Integer(), nullable=False),
		sa.Column("text", sa.Text, nullable=False),
		sa.Column("rating", sa.Integer, nullable=False),
		sa.Column(
			"date",
			sa.DateTime(timezone=True),
			nullable=False,
			server_default=sa.text("now()"),
		),
		sa.Column("ai_sentiment", sa.String(50), nullable=True),
		sa.Column("ai_confidence", sa.Float, nullable=True),
		sa.Column("ai_scores", sa.JSON(), nullable=True),
		sa.Column("ai_postprocess_meta", sa.JSON(), nullable=True),
		sa.Column("analysis_source", sa.String(50), nullable=True),
		sa.ForeignKeyConstraint(
			["user_id"], ["users.id"], ondelete="CASCADE"
		),
	)
