from sqlalchemy import Column, Integer, DateTime, func, ForeignKey, String, Table
from sqlalchemy.orm import relationship

from .base import Base


image_m2m_tag = Table(
    "note_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = "images"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="images")

    url = Column(String(200))
    identifier = Column(String(40), unique=True)
    description = Column(String(250))

    tags = relationship("Tag", secondary=image_m2m_tag, backref="images")

    comments = relationship("Comment", back_populates="image")
    
class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())

    name = Column(String(25), nullable=False, unique=True)

