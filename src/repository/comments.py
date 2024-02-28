from sqlalchemy.orm import Session
from ..schemas.comment_example import CommentCreate, Comment

from .base_repository import AbstractRepository
from ..models.comment import Comment
from ..models.user import User, Role


class CommentsRepo(AbstractRepository):
    model = Comment

    def __init__(self, user: User, db: Session) -> None:
        self.user = user
        super().__init__(db)

    async def create(self, body: str, image_id: int, user_id: int):
        """
        The create function creates a new comment in the database.
                Args:
                    body (str): The body of the comment.
                    image_id (int): The id of the image that this comment is associated with. 
                    This is used to associate comments with images, and also to retrieve all comments for an image when needed.
                    user_id (int): The id of the user who created this comment.
        
        :param self: Represent the instance of the class
        :param body: str: Create the body of the comment
        :param image_id: int: Specify the image that the comment is being made on
        :param user_id: int: Identify the user that is creating the comment
        :return: A new comment object
        :doc-author: Trelent
        """
        new_comment = Comment(
            body=body, 
            image_id=image_id,
            user_id=user_id
        )
        self.db.add(new_comment)
        self.db.commit()
        self.db.refresh(new_comment)
        return new_comment
    
    async def get_single(self, image_id: int, comment_id: int):
        """
        The get_single function is used to retrieve a single comment from the database.
            
        
        :param self: Represent the instance of the class
        :param image_id: int: Filter the comments by image_id
        :param comment_id: int: Get the comment from the database using its id
        :return: A comment object
        :doc-author: Trelent
        """
        comment = self.db.query(Comment).filter(Comment.id == comment_id, Comment.image_id == image_id).first()
        if comment is not None:
            return comment

    async def get_many(self, image_id: int):
        """
        The get_many function returns all comments associated with a given image_id.
            
        
        :param self: Represent the instance of the class
        :param image_id: int: Filter the comments by image_id
        :return: A list of comments that are associated with the image_id
        :doc-author: Trelent
        """
        return self.db.query(Comment).filter(Comment.image_id == image_id).all()

    async def update(self, image_id: int, comment_id: int, new_body: str):
        """
        The update function updates the body of a comment.
            
        
        :param self: Represent the instance of the class
        :param image_id: int: Find the image that the comment is attached to
        :param comment_id: int: Identify the comment to be updated
        :param new_body: str: Update the comment body
        :return: A comment object
        :doc-author: Trelent
        """
        comment = self.db.query(Comment).filter(Comment.id == comment_id, Comment.image_id == image_id).first()
        if comment is not None:
            comment.body = new_body
            self.db.commit()
            self.db.refresh(comment)
            return comment
        return None

    async def delete(self, image_id: int,  comment_id: int):
        """
        The delete function deletes a comment from the database.
            
        
        :param self: Represent the instance of the class
        :param image_id: int: Filter the comment to be deleted
        :param comment_id: int: Specify which comment to delete
        :return: True if the comment is deleted and false if the comment doesn't exist
        :doc-author: Trelent
        """
        comment = self.db.query(Comment).filter(Comment.id == comment_id, Comment.image_id == image_id).first()
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False

    async def can_edit_comment(self, user: User, comment: Comment) -> bool:
        """
        The can_edit_comment function determines whether a user can edit a comment.
        
        A user can edit their own comments, but not other users' comments.
        
        
        :param self: Represent the instance of the class
        :param user: User: Get the user id of the comment author
        :param comment: Comment: Check if the user is the author of the comment
        :return: A boolean value
        :doc-author: Trelent
        """
        return user.id == comment.user_id
    
    async def can_delete_comment(self, user: User) -> bool:
        """
        The can_delete_comment function determines whether a user can delete a comment.
                
        
        :param self: Represent the instance of the class
        :param user: User: Determine the role of the user who is trying to delete a comment
        :return: A boolean value
        :doc-author: Trelent
        """
        return user.role in {Role.admin, Role.moderator}
