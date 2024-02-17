from fastapi import FastAPI, Depends, HTTPException
from typing import List
from ..models import comment
from ..schemas import comment_example

from ..repository.comments import create_comment, get_comments_for_image
from ..dependencies.db import get_db, SessionLocal

app = FastAPI()

@app.post("/images/{image_id}/comments/", response_model=comment_example.CommentDisplay)
def create_comment_for_image(
    image_id: int, comment: comment_example.CommentCreate, db: SessionLocal = Depends(get_db)
):
    return comment.create_comment(db=db, comment=comment, image_id=image_id)

@app.get("/images/{image_id}/comments/", response_model=List[comment_example.CommentDisplay])
def read_comments_for_image(image_id: int, db: SessionLocal = Depends(get_db)):
    return comment.get_comments_for_image(db=db, image_id=image_id)
