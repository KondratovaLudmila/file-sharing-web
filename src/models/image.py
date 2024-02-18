from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.orm import relationship

from .base import Base

class Image(Base):
    __tablename__ = "images"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    filename = Column(String, index=True)
    comments = relationship("Comment", back_populates="image")


#Tags and image_m2m_tag here

