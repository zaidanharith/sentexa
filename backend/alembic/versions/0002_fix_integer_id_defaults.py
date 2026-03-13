from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS reviews CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), sa.Identity(start=1), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column(
            "date",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("ai_sentiment", sa.String(50), nullable=True),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

def downgrade() -> None:
    op.drop_table("reviews")
    op.drop_table("users")
