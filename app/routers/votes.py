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
        Vote.post_id == vote_data.post_id, Vote.user_id == current_user.id
    )
    db_vote = session.exec(query).first()
    db_post = session.get(Post, vote_data.post_id)
    if not db_post:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {vote_data.post_id} does not exist!",
        )

    # Undo existing vote
    if vote_data.vote_dir == VoteDirection.NO_VOTE:
        if not db_vote:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Vote not found: User has not yet voted on post {db_post.id}!",
            )
        session.delete(db_vote)
        session.commit()
        return VoteResponse(message="Removed vote!")

    # Upvote or downvote
    else:
        # Cannot vote on own post
        if current_user.id == db_post.author_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                                detail="Users cannot vote on their own post!")
        
        # Cannot vote twice
        if db_vote:
            # If user wants to change vote direction:
            if db_vote.vote_type != vote_data.vote_dir:
                db_vote.vote_type = vote_data.vote_dir
                commit_and_refresh(session, db_vote)
                return VoteResponse(message="Vote changed successfully!")

            # if same vote direction as before: error
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"User has already voted on post {db_post.id}!",
            )
        # Create a new vote
        new_vote = Vote(
            post_id=vote_data.post_id,
            user_id=current_user.id,
            vote_type=vote_data.vote_dir,
        )
        session.add(new_vote)
        commit_and_refresh(session, new_vote)
        return VoteResponse(message="Voted successfully!")
