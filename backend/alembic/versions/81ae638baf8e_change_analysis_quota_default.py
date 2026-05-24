"""change_analysis_quota_default

Revision ID: 81ae638baf8e
Revises: 48111258a37b
Create Date: 2026-05-24 14:03:47.297858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '81ae638baf8e'
down_revision: Union[str, None] = '48111258a37b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'analysis_quota', server_default='5')


def downgrade() -> None:
    op.alter_column('users', 'analysis_quota', server_default='100')
