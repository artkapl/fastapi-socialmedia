"""add author foreign key to post

Revision ID: 73fc94f27c8f
Revises: 8d32519b5960
Create Date: 2025-02-01 20:06:36.071451

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73fc94f27c8f'
down_revision: Union[str, None] = '8d32519b5960'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "post",
        sa.Column("author_id", sa.Integer(), nullable=False)
    )
    op.create_foreign_key(
        constraint_name="post_author_id_fkey",
        source_table="post",
        referent_table="user",
        local_cols=["author_id"],
        remote_cols=["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_column("post", "author_id")
