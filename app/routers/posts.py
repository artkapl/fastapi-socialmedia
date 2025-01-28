from typing import Annotated
from datetime import UTC, datetime

from fastapi import Depends, APIRouter, HTTPException, Query, Response, status
from sqlmodel import Field, or_, select, col
from app.core.database import SessionDep, commit_and_refresh

from app.models.posts import Post, PostCreate, PostPublicWithUser, PostUpdate
from app.core.security import CurrentUser


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
        search_title_or_content = or_(
            col(Post.title).contains(q), col(Post.content).contains(q)
        )
        query = select(Post).where(search_title_or_content).offset(offset).limit(limit)
    posts = session.exec(query).all()
    return posts


@router.get("/{id}", response_model=PostPublicWithUser)
def get_post(id: int, session: SessionDep) -> Post:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(
    post: PostCreate, session: SessionDep, current_user: CurrentUser
) -> Post:
    # Convert PostCreate object to Post in DB
    author_dict = {"author_id": current_user.id}
    db_post = Post.model_validate(post, update=author_dict)
    # Store Post in DB
    session.add(db_post)
    commit_and_refresh(session, db_post)
    return db_post


@router.patch("/{id}", response_model=Post)
def update_post(
    id: int, post: PostUpdate, session: SessionDep, current_user: CurrentUser
) -> Post:
    # get post by ID
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # User can only edit their own posts (admin can do all)
    if not current_user.is_superuser and current_user != db_post.author:
        raise HTTPException(
            status_code=403, detail="You are not allowed to change someone else's post"
        )

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
        raise HTTPException(
            status_code=403, detail="You are not allowed to delete someone else's post"
        )

    session.delete(db_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
