"""update users subscription fields

Revision ID: 0011
Revises: 0010
Create Date: 2026-05-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0011"
down_revision: Union[str, None] = "0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	# Rename subscription to subscription_plan
	op.alter_column("users", "subscription", new_column_name="subscription_plan")
	
	# Rename subscription_quota_remaining to analysis_quota
	op.alter_column("users", "subscription_quota_remaining", new_column_name="analysis_quota")
	
	# Rename subscription_expires_at to subscription_end
	op.alter_column("users", "subscription_expires_at", new_column_name="subscription_end")
	
	# Add subscription_status column
	op.add_column(
		"users",
		sa.Column(
			"subscription_status",
			sa.String(50),
			nullable=False,
			server_default="active",
		),
	)
	
	# Add subscription_start column
	op.add_column(
		"users",
		sa.Column(
			"subscription_start",
			sa.DateTime(timezone=True),
			nullable=True,
		),
	)


def downgrade() -> None:
	# Remove subscription_start
	op.drop_column("users", "subscription_start")
	
	# Remove subscription_status
	op.drop_column("users", "subscription_status")
	
	# Rename back subscription_end to subscription_expires_at
	op.alter_column("users", "subscription_end", new_column_name="subscription_expires_at")
	
	# Rename back analysis_quota to subscription_quota_remaining
	op.alter_column("users", "analysis_quota", new_column_name="subscription_quota_remaining")
	
	# Rename back subscription_plan to subscription
	op.alter_column("users", "subscription_plan", new_column_name="subscription")
