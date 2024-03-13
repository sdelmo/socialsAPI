from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
# Create instance

app = FastAPI()

my_posts = [
    {"title": "post1", "content": "aaa", "id": 1},
    {"title": "post2", "content": "bbb", "id": 2},
    {"title": "post3", "content": "ccc", "id": 123}
]


def find_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return p, i


class Post(BaseModel):

    title: str
    content: str
    published: bool = True

# Use a try/except in case conection fails


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi',
                                user='postgres', password='q765', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('DB connection successful')
        break

    except Exception as e:
        print(f"Connecting to DB failed\nError was {e}")
        time.sleep(2)


@app.get("/")
async def root():
    return {"message": "Welcome to api"}


# Retrieve social media posts

@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()

    return {"data": new_post}


# Id is a path parameter, hence embedded in url
@app.get("/posts/{id}")
def get_post(id: int, response: Response):

    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))

    found_post = cursor.fetchone()

    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return {"post_detail": found_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):

    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))

    deleted_post = cursor.fetchone()
    conn.commit()

    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %sRETURNING *""",
                   (post.title, post.content, post.published, (str(id))))
    updated_post = cursor.fetchone()

    conn.commit()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return {"data": updated_post}
