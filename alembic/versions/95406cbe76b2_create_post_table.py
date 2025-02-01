"""create posts table

Revision ID: 95406cbe76b2
Revises: 
Create Date: 2025-02-01 19:11:17.552081

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel.sql.sqltypes
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95406cbe76b2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("published", sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(), 
                  server_default=sa.text("(now() at time zone('utc'))"), 
                  nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP()),
        sa.PrimaryKeyConstraint("id"),
    )



def downgrade() -> None:
    op.drop_table("post")
