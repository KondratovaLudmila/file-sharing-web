from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    body = Column(Text, nullable=False)

    image_id = Column(Integer, ForeignKey('images.id'))  
    image = relationship("Image", back_populates="comments")

    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="comments")