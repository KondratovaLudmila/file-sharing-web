from fastapi import Depends
from sqlalchemy.orm import Session
from ..dependencies.db import get_db
from ..models.user import User

# Temporary mock untill auth not implemented
def get_user(db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username=='admin').first()

    if not user:
        user = User(username="admin", password="1234", email="admin@gmail.com", confirmed=True, role='admin')
        db.add(user)
        db.commit()
        db.refresh(user)

    return user