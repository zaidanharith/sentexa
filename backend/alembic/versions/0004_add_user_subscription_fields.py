from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "subscription",
            sa.String(length=50),
            nullable=False,
            server_default="free",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "subscription_quota_remaining",
            sa.Integer(),
            nullable=False,
            server_default="100",
        ),
    )
    op.add_column(
        "users",
        sa.Column("subscription_expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "subscription_expires_at")
    op.drop_column("users", "subscription_quota_remaining")
    op.drop_column("users", "subscription")