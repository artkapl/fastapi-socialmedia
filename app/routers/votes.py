from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from app.core.database import SessionDep, commit_and_refresh
from app.models.posts import Post

from app.models.votes import Vote, VoteData, VoteDirection, VoteResponse
from app.core.security import CurrentUser


router = APIRouter(prefix="/vote", tags=["Votes"])


@router.post("/")
def cast_vote(vote_data: VoteData, session: SessionDep, current_user: CurrentUser):
    # Get vote from DB if exists
    query = select(Vote).where(
        Vote.post_id == vote_data.post_id and Vote.user_id == current_user.id
    )
    db_vote = session.exec(query).first()

    # Undo existing vote
    if vote_data.vote_dir == VoteDirection.NO_VOTE:
        if not db_vote:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Vote not found: User has not yet voted on this post!",
            )
        session.delete(db_vote)
        session.commit()
        return VoteResponse(message="Removed vote!")

    # Upvote or downvote
    else:
        # Cannot vote on own post
        db_post = session.get(Post, vote_data.post_id)
        if current_user.id == db_post.author_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Users cannot vote on their own post!")
        
        # Cannot vote twice
        if db_vote:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User has already voted on this post!",
            )
        new_vote = Vote(
            post_id=vote_data.post_id,
            user_id=current_user.id,
            vote_type=vote_data.vote_dir,
        )
        session.add(new_vote)
        commit_and_refresh(session, new_vote)
        return VoteResponse(message="Voted successfully!")

