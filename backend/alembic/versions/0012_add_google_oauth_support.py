"""add google oauth support

Revision ID: 0012
Revises: 0011
Create Date: 2026-05-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0012"
down_revision: Union[str, None] = "0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	# Make password nullable for social login
	op.alter_column(
		"users",
		"password",
		existing_type=sa.String(255),
		nullable=True,
	)
	
	# Add google_id column
	op.add_column(
		"users",
		sa.Column(
			"google_id",
			sa.String(255),
			nullable=True,
		),
	)
	
	# Create unique constraint on google_id
	op.create_unique_constraint(
		"uq_users_google_id",
		"users",
		["google_id"],
	)


def downgrade() -> None:
	# Drop unique constraint
	op.drop_constraint(
		"uq_users_google_id",
		"users",
	)
	
	# Remove google_id column
	op.drop_column("users", "google_id")
	
	# Make password not nullable again
	op.alter_column(
		"users",
		"password",
		existing_type=sa.String(255),
		nullable=False,
	)
