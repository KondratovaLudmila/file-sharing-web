from fastapi import APIRouter, HTTPException, Depends, status, Response
from typing import List
from sqlalchemy.orm import Session

from ..schemas.comment_example import CommentCreate, Comment
from ..dependencies.db import get_db
from ..repository.comments import CommentsRepo
from ..models.user import User

router = APIRouter(prefix='/images', tags=["comments"])


@router.post("/{image_id}/comments/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment_for_image(
    image_id: int, 
    comment_data: CommentCreate, 
    db: Session = Depends(get_db)
):
    # Temporary before we have users
    user = db.get(User, 1)
    if not user:
        db.add(User(username="vasya", password="1234", email="vasya@gmail.com", confirmed=True))
        db.commit()

    comment = await CommentsRepo(user, db).create(image_id, comment_data.body)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found for comment!")
    
    return comment


@router.get("/{image_id}/comments/", response_model=List[Comment])
async def read_comments_for_image(
    image_id: int, 
    db: Session = Depends(get_db)
):
    comments = await CommentsRepo(db).get_many(image_id)
    return comments


@router.patch("/comments/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: int, 
    comment_data: Comment, 
    db: Session = Depends(get_db)
):
    user = db.get(User, 1)  # Temporary
    updated_comment = await CommentsRepo(user, db).update(comment_id, comment_data.body)
    
    if not updated_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!")
    
    return updated_comment


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db)
):
    user = db.get(User, 1)  # Temporary
    success = await CommentsRepo(user, db).delete(comment_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)