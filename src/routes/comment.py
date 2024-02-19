from fastapi import APIRouter, HTTPException, Depends, status, Response
from typing import List
from sqlalchemy.orm import Session

from ..schemas.comment_example import CommentCreate, Comment
from ..dependencies.db import get_db
from ..repository.comments import CommentsRepo
from ..models.user import User
from ..repository.images import Images as ImagesRepo

router = APIRouter(prefix='/images', tags=["comments"])


@router.post("/{image_id}/comments/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment_for_image(
    comment_data: CommentCreate, 
    image_id: int, 
    db: Session = Depends(get_db)
):
    comment = await CommentsRepo(User, db).create(comment_data, image_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found for comment!")

    return comment


@router.get("/{image_id}/comment/{comment_id}", response_model=Comment)
async def read_comment_for_image(
    image_id: int, 
    comment_id: int,
    db: Session = Depends(get_db)
):
    comments = await CommentsRepo(User, db).get_single(image_id, comment_id)
    return comments


@router.get("/{image_id}/comments/", response_model=List[Comment])
async def read_all_comments_for_image(
    image_id: int, 
    db: Session = Depends(get_db)
):
    comments = await CommentsRepo(User, db).get_many(image_id)
    return comments


@router.patch("/{image_id}/comments/{comment_id}", response_model=Comment)
async def update_comment(
    image_id: int, 
    comment_id: int, 
    comment_data: Comment, 
    db: Session = Depends(get_db)
):
    updated_comment = await CommentsRepo(User, db).update(image_id, comment_id, comment_data.body)

    if not updated_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!")

    return updated_comment


@router.delete("/{image_id}/comments/{comment_id}")
async def delete_comment(
    image_id: int, 
    comment_id: int, 
    db: Session = Depends(get_db)
):
    success = await CommentsRepo(User, db).delete(image_id, comment_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!")

    return Response(status_code=status.HTTP_204_NO_CONTENT)