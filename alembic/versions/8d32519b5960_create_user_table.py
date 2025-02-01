"""create user table

Revision ID: 8d32519b5960
Revises: 95406cbe76b2
Create Date: 2025-02-01 19:38:32.232620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d32519b5960'
down_revision: Union[str, None] = '95406cbe76b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String()),
        sa.Column("last_name", sa.String()),
        sa.Column("email", sa.String(), unique=True, nullable=False),
        sa.Column("is_superuser", sa.Boolean(), default=False, nullable=False),
        sa.Column("password_crypt", sa.String(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), 
                  server_default=sa.text("(now() at time zone('utc'))"), 
                  nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade() -> None:
    op.drop_table("user")
