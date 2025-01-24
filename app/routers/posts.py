from typing import Annotated
from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException, Query, Response, status
from sqlmodel import Field, select
from app.database import SessionDep, commit_and_refresh

from app.models.posts import Post, PostCreate, PostUpdate


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[Post])
def get_posts_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    posts = session.exec(select(Post).offset(offset).limit(limit)).all()
    return posts


@router.get("/{id}", response_model=Post)
def get_post(id: int, session: SessionDep):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(post: PostCreate, session: SessionDep):
    # Convert PostCreate object to Post in DB
    db_post = Post.model_validate(post)
    # Store Post in DB
    session.add(db_post)
    commit_and_refresh(session, db_post)
    return db_post


@router.patch("/{id}", response_model=Post)
def update_post(id: int, post: PostUpdate, session: SessionDep):
    # get post by ID
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    # Update post with Update values
    updated_data = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(updated_data)
    # Set update time
    db_post.updated_at = datetime.now(datetime.UTC)
    # Commit to DB
    session.add(db_post)
    commit_and_refresh(session, db_post)
    return db_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep):
    # get post by ID
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(db_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
