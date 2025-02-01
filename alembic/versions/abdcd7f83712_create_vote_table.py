"""create vote table

Revision ID: abdcd7f83712
Revises: 73fc94f27c8f
Create Date: 2025-02-01 20:29:13.692228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.models.votes import VoteDirection


# revision identifiers, used by Alembic.
revision: str = 'abdcd7f83712'
down_revision: Union[str, None] = '73fc94f27c8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    vote_type = postgresql.ENUM(VoteDirection, name="votedirection")
    vote_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "vote",
        sa.Column("post_id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False, primary_key=True),
    )
    op.add_column("vote", sa.Column("vote_type", vote_type, nullable=False)),
    op.create_foreign_key(
        constraint_name="vote_post_id_fkey",
        source_table="vote",
        referent_table="post",
        local_cols=["post_id"],
        remote_cols=["id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "vote_user_id_fkey",
        "vote",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint("vote_user_id_fkey", "vote")
    op.drop_constraint("vote_post_id_fkey", "vote")
    op.drop_table("vote")
