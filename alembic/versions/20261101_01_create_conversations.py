"""create conversations table

Revision ID: 20261101_01
Revises: 20261026_01
Create Date: 2026-11-01 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261101_01"
down_revision: str | None = "20261026_01"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_email", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_user_email", "conversations", ["user_email"])


def downgrade() -> None:
    op.drop_index("ix_conversations_user_email", table_name="conversations")
    op.drop_table("conversations")
