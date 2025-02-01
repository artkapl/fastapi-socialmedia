from enum import Enum
from sqlmodel import Relationship, Field, SQLModel


class VoteDirection(Enum):
    DOWNVOTE: int = -1
    NO_VOTE: int = 0
    UPVOTE: int = 1


class Vote(SQLModel, table=True):
    __tablename__ = "vote"

    post_id: int = Field(foreign_key="post.id", primary_key=True, ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", primary_key=True, ondelete="CASCADE")

    vote_type: VoteDirection = Field(default=VoteDirection.NO_VOTE)


class VoteData(SQLModel):
    post_id: int
    vote_dir: VoteDirection


class VoteResponse(SQLModel):
    message: str
