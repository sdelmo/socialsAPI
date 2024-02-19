from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
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
    rating: Optional[int] = None

# A path operation


@app.get("/")
async def root():
    return {"message": "Welcome to api"}


# Retrieve social media posts

@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 10000000)
    my_posts.append(post_dict)
    return {"data": post_dict} if post.published else None


# Id is a path parameter, hence embedded in url
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    print(id)
    found, i = find_post(id)

    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return {"post_detail": found}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):

    try:
        found, i = find_post(id)
        my_posts.pop(i)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    print(post)

    try:
        found, i = find_post(id)
        my_posts[i] = post.model_dump()
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} not found")
    return {'message': f"updated post with  id: {id} to {my_posts[i]}"}
