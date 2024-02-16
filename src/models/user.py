from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey
from sqlalchemy.orm import relationship

#required import for each table
from .base import Base

class User(Base):
    __tablename__ = "users"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    password = Column(String)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())