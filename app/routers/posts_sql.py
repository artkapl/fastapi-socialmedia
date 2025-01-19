from functools import lru_cache
from fastapi import APIRouter, HTTPException, status, Response
import psycopg
from psycopg.rows import dict_row

from ..config import Settings

from ..schema import Post, PostRequest


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

router = APIRouter(prefix="/posts")


while True:
    try:
        conn = psycopg.connect(
            f"dbname={settings.db_name} port={settings.db_port} user={settings.db_user} password={settings.db_password}"
        )
        cur = conn.cursor(row_factory=dict_row)
        print("Connection to database successful!")
        break
    except Exception as e:
        print("Error connecting to database")
        print(e)


@router.get("/")
async def get_posts() -> list[Post]:
    posts = cur.execute(""" SELECT * FROM posts """).fetchall()
    return posts


@router.get("/{id}", responses={404: {"description": "Not Found"}})
async def get_post(id: int) -> Post:
    post = cur.execute(""" SELECT * FROM posts WHERE id = %s""", (id,)).fetchone()
    if not post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostRequest):
    cur.execute(
        """ INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
        (post.title, post.content, post.published),
    )
    new_post = cur.fetchone()
    conn.commit()
    return {"message": "Post created!", "data": new_post}


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Not Found"}},
)
async def delete_post(id: int):
    cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (id,))
    deleted_post = cur.fetchone()
    if not deleted_post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Not Found"}},
)
async def update_post(id: int, post: PostRequest):
    cur.execute(
        """ UPDATE posts SET title = %(title)s, content = %(content)s, published = %(published)s, updated_at = %(updated_at)s WHERE id = %(id)s RETURNING * """,
        {
            "title": post.title,
            "content": post.content,
            "published": post.published,
            "updated_at": "NOW()",
            "id": id,
        },
    )
    updated_post = cur.fetchone()
    if not updated_post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
