from functools import lru_cache
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Response, status
import psycopg
from psycopg.rows import dict_row

import config
from schema import Post


@lru_cache
def get_settings():
    return config.Settings()


settings = get_settings()
app = FastAPI()

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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/posts")
async def get_posts():
    posts = cur.execute(""" SELECT * FROM posts """).fetchall()
    return posts


@app.get("/posts/{id}")
async def get_post(id: int):
    post = cur.execute(""" SELECT * FROM posts WHERE id = %s""", (id,)).fetchone()
    if not post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    return post


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    cur.execute(
        """ INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
        (post.title, post.content, post.published),
    )
    new_post = cur.fetchone()
    conn.commit()
    return {"message": "Post created!", "data": new_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int):
    cur.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (id,))
    deleted_post = cur.fetchone()
    if not deleted_post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_post(id: int, post: Post):
    cur.execute(""" UPDATE posts SET title = %(title)s, content = %(content)s, published = %(published)s, updated_at = %(updated_at)s WHERE id = %(id)s RETURNING * """, 
                {"title": post.title, "content": post.content, "published": post.published, "updated_at": "NOW()", "id": id})
    updated_post = cur.fetchone()
    if not updated_post:
        raise HTTPException(404, f"Post with ID {id} not found!")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/info", description="Get detailed database information", name="Get DB Info")
async def info(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {
        "app_name": settings.app_name,
        "db_host": settings.db_host,
        "db_name": settings.db_name,
    }
