from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db
models.Base.metadata.create_all(bind=engine)

# Create instances

app = FastAPI()


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
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()

    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # Create a new post

    new_post = models.Post(
        **post.model_dump())

    # Add new post to db
    db.add(new_post)
    # Commit the new post
    db.commit()

    # Return the post i just created
    db.refresh(new_post)

    return {"data": new_post}


# Id is a path parameter, hence embedded in url
@app.get("/posts/{id}")
def get_post(id: int, response: Response, db: Session = Depends(get_db)):

    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))

    # found_post = cursor.fetchone()

    # Filter is like a where statement
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response, db: Session = Depends(get_db)):

    # cursor.execute(
    #     """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))

    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %sRETURNING *""",
    #                (post.title, post.content, post.published, (str(id))))
    # updated_post = cursor.fetchone()

    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    acc_post = post_query.first()

    if not acc_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    post_query.update(post.model_dump(), synchronize_session=False)

    db.commit()

    return {"data": post_query.first()}
