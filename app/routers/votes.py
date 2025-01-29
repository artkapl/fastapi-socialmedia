from typing import Annotated
from datetime import UTC, datetime

from fastapi import Depends, APIRouter, HTTPException, Query, Response, status
from sqlmodel import Field, or_, select, col
from app.core.database import SessionDep, commit_and_refresh

from app.models.votes import Vote, VoteData
from app.core.security import CurrentUser


router = APIRouter(prefix="/votes", tags=["Votes"])


@router.post("/")
def cast_vote(vote_data: VoteData, session: SessionDep, current_user: CurrentUser):
    # Get vote from DB if exists
    query = select(Vote).where(
        Vote.post_id == vote_data.post_id and Vote.user_id == current_user.id
    )
    db_vote = session.exec(query)

    # Undo existing vote
    if vote_data.vote_dir == 0:
        if not db_vote:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Cannot undo vote: User has not yet voted on this post!",
            )
        session.delete(db_vote)
        session.commit()
    # Upvote or downvote
    else:
        db_vote = session.exec(query)
        if db_vote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already voted on this post!",
            )
        new_vote = Vote(
            post_id=vote_data.post_id,
            user_id=current_user.id,
            vote_type=vote_data.vote_dir,
        )
        session.add(new_vote)
        commit_and_refresh(session, new_vote)
    return Response("Voted successfully!", status_code=201)
