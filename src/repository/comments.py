from sqlalchemy.orm import Session
from ..schemas.comment_example import CommentCreate, Comment

from .base_repository import AbstractRepository
from ..models.comment import Comment
from ..models.user import User


class CommentsRepo(AbstractRepository):
    model = Comment

    def __init__(self, user: User, db: Session) -> None:
        self.user = user
        super().__init__(db)

    async def create(self, comment_data: CommentCreate, image_id: int):
        new_comment = Comment(body=comment_data.body, image_id=image_id, user_id=self.user.id)
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        return new_comment

    async def get_many(self, image_id: int):
        return self.db.query(Comment).filter(Comment.image_id == image_id).all()

    async def update(self, comment_id: int, new_body: str):
        comment = self.db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == self.user.id).first()
        if comment:
            comment.body = new_body
            self.db.commit()
            self.db.refresh(comment)
            return comment
        return None

    async def delete(self, comment_id: int):
        comment = self.db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == self.user.id).first()
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False
