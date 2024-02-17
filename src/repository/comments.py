from ..dependencies.db import SessionLocal
from ..models import comment
from ..schemas import comment_example


def create_comment(db: SessionLocal, comment: comment_example.CommentCreate, image_id: int):
    db_comment = comment_example.Comment(body=comment.body, image_id=image_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_for_image(db: SessionLocal, image_id: int):
    return db.query(comment.Comment).filter(comment.Comment.image_id == image_id).all()
