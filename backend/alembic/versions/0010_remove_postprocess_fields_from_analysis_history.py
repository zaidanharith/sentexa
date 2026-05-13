"""remove postprocess fields from analysis_history

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	op.drop_column("analysis_history", "include_meta")
	op.drop_column("analysis_history", "apply_postprocess")


def downgrade() -> None:
	op.add_column(
		"analysis_history",
		sa.Column("apply_postprocess", sa.Boolean(), nullable=False, server_default=sa.text("true")),
	)
	op.add_column(
		"analysis_history",
		sa.Column("include_meta", sa.Boolean(), nullable=False, server_default=sa.text("false")),
	)
