from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, and_

from app.core.database import SessionDep, commit_and_refresh
from app.models.posts import Post
from app.models.votes import Vote, VoteData, VoteDirection, VoteResponse
from app.core.security import CurrentUser


router = APIRouter(prefix="/vote", tags=["Votes"])

# Response message constants
VOTE_REMOVED = "Removed vote!"
VOTE_CHANGED = "Vote changed successfully!"
VOTE_CREATED = "Voted successfully!"
POST_NOT_FOUND = "Post with id {post_id} does not exist!"
CANNOT_VOTE_OWN = "Users cannot vote on their own post!"
ALREADY_VOTED = "User has already voted on post {post_id}!"


@router.post("/", response_model=VoteResponse)
def cast_vote(vote_data: VoteData, session: SessionDep, current_user: CurrentUser) -> VoteResponse:
    # Get vote from DB if exists
    query = select(Vote).where(and_(Vote.post_id == vote_data.post_id, Vote.user_id == current_user.id))
    db_vote = session.exec(query).first()
    db_post = session.get(Post, vote_data.post_id)
    if not db_post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=POST_NOT_FOUND.format(post_id=vote_data.post_id))

    # Undo existing vote
    if vote_data.vote_dir == VoteDirection.NO_VOTE:
        if db_vote:
            session.delete(db_vote)
            session.commit()
        return VoteResponse(message=VOTE_REMOVED)

    if current_user.id == db_post.author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=CANNOT_VOTE_OWN)

    if db_vote:
        if db_vote.vote_type != vote_data.vote_dir:
            db_vote.vote_type = vote_data.vote_dir
            commit_and_refresh(session, db_vote)
            return VoteResponse(message=VOTE_CHANGED)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=ALREADY_VOTED.format(post_id=db_post.id))

    # Create a new vote
    new_vote = Vote(post_id=vote_data.post_id, user_id=current_user.id, vote_type=vote_data.vote_dir)
    session.add(new_vote)
    commit_and_refresh(session, new_vote)
    return VoteResponse(message=VOTE_CREATED)
