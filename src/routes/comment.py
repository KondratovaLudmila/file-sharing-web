from fastapi import APIRouter, HTTPException, Depends, status, Response, Body, Path
from typing import List
from sqlalchemy.orm import Session

from ..schemas.comment_example import CommentCreate, Comment
from ..dependencies.db import get_db
from ..repository.comments import CommentsRepo
from ..models.user import User
from ..repository.images import Images as ImagesRepo
from ..services.auth import get_current_user

router = APIRouter(prefix='/images', tags=["comments"])


@router.post("/{image_id}/comments/", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_comment_for_image(
    body: str = Body(..., description="The content of the comment"),
    image_id: int = Path(..., description="The ID of the image"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    comment = await CommentsRepo(User, db).create(body, image_id, current_user.id)
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
    image_id: int = Path(..., description="The ID of the image"),
    comment_id: int = Path(..., description="The ID of the comment"),
    body: str = Body(..., description="New body of the comment"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    comments_repo = CommentsRepo(User, db)
    comment = await comments_repo.get_single(image_id, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if not await comments_repo.can_edit_comment(current_user, comment):
        raise HTTPException(status_code=403, detail="You don't have permission to edit this comment")

    updated_comment = await comments_repo.update(image_id, comment_id, body)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Failed to update comment")

    return updated_comment


@router.delete("/{image_id}/comments/{comment_id}", response_model=Comment)
async def delete_comment(
    image_id: int, 
    comment_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    comment_repo = CommentsRepo(User, db)

    if not await comment_repo.can_delete_comment(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this comment!")

    comment = await comment_repo.get_single(image_id, comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found!")

    success = await comment_repo.delete(image_id, comment_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to delete comment!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)