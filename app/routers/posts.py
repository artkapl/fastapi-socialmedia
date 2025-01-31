from typing import Annotated
from datetime import UTC, datetime

from fastapi import Depends, APIRouter, HTTPException, Query, Response, status
from sqlmodel import Field, or_, select, col, func
from app.core.database import SessionDep, commit_and_refresh

from app.models.posts import Post, PostCreate, PostPublicWithUser, PostUpdate
from app.core.security import CurrentUser
from app.models.votes import Vote, VoteDirection


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[PostPublicWithUser])
def get_posts_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    q: Annotated[str | None, Query(alias="search")] = None,
) -> list[Post]:
    query = select(Post).offset(offset).limit(limit)
    if q:
        search_title_or_content = or_(col(Post.title).contains(q), col(Post.content).contains(q))
        query = select(Post).where(search_title_or_content).offset(offset).limit(limit)
    posts = session.exec(query).all()

    # get votes
    post_ids = [post.id for post in posts]
    post_votes = get_votes_count(post_ids, session)

    # Update Post response with number of upvotes & downvotes
    for idx, post in enumerate(posts):
        post_vote_dict = {"num_upvotes": 0, "num_downvotes": 0}
        if post_count := post_votes.get(post.id):
            post_vote_dict = {
                "num_upvotes": post_count.get("num_upvotes", 0),
                "num_downvotes": post_count.get("num_downvotes", 0),
            }
        posts[idx] = PostPublicWithUser.model_validate(post, update=post_vote_dict)

    return posts


@router.get("/{id}", response_model=PostPublicWithUser)
def get_post(id: int, session: SessionDep) -> Post:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    # Get votes for post
    votes = get_votes_count([post.id], session)
    # Update post response to include upvotes & downvotes
    post_vote_dict = {
        "num_upvotes": votes.get(post.id, {}).get("num_upvotes", 0),
        "num_downvotes": votes.get(post.id, {}).get("num_downvotes", 0),
    }
    post = PostPublicWithUser.model_validate(post, update=post_vote_dict)
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(post: PostCreate, session: SessionDep, current_user: CurrentUser) -> Post:
    # Convert PostCreate object to Post in DB
    author_dict = {"author_id": current_user.id}
    db_post = Post.model_validate(post, update=author_dict)
    # Store Post in DB
    session.add(db_post)
    commit_and_refresh(session, db_post)
    return db_post


@router.patch("/{id}", response_model=Post)
def update_post(id: int, post: PostUpdate, session: SessionDep, current_user: CurrentUser) -> Post:
    # get post by ID
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # User can only edit their own posts (admin can do all)
    if not current_user.is_superuser and current_user != db_post.author:
        raise HTTPException(status_code=403, detail="You are not allowed to change someone else's post")

    # Update post with Update values
    updated_data = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(updated_data)
    # Set update time
    db_post.updated_at = datetime.now(UTC)
    # Commit to DB
    session.add(db_post)
    commit_and_refresh(session, db_post)
    return db_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep, current_user: CurrentUser) -> Response:
    # get post by ID
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # User can only delete their own posts (admin can do all)
    if not current_user.is_superuser and current_user != db_post.author:
        raise HTTPException(status_code=403, detail="You are not allowed to delete someone else's post")

    session.delete(db_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def get_votes_count(post_ids: list[int], session: SessionDep) -> dict:
    votes_dict = {}
    vote_query = (
        select(Vote.post_id, Vote.vote_type, func.count(Vote.post_id))
        .where(Vote.post_id.in_(post_ids))
        .group_by(Vote.post_id, Vote.vote_type)
        .order_by(Vote.post_id)
    )
    votes = session.exec(vote_query).all()

    # get upvotes & downvotes
    for post in votes:
        post_id = post[0]
        vote_dir = "num_upvotes" if post[1].name == "UPVOTE" else "num_downvotes"
        num_votes = post[2]

        if votes_dict.get(post[0]):
            votes_dict[post_id].update({vote_dir: num_votes})
        else:
            votes_dict[post_id] = {vote_dir: num_votes}
    return votes_dict
