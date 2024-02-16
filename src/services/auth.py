from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from models import user
from typing import List

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
DATABASE_URL = "sqlite:///./test.db"

#tokenchecker
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#create_db_connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#get_db_session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#get_user_by_name
def get_user(username: str, db_session: Session):
    return db_session.query(user).filter(user.name == username).first()

#passchecker
def verify_password(plain_password, hashed_password):
    # Реалізуйте логіку перевірки паролю за необхідності
    return plain_password == hashed_password

#jwt_func
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

#auth_and_get_current_user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Can't validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return get_user(username, db)

#jwt_token
@app.post("/token")
async def login_for_access_token(form_data: dict, db: Session = Depends(get_db)):
    username = form_data["username"]
    password = form_data["password"]
    user = get_user(username, db)
    if user and verify_password(password, user.password):
        token_data = {"sub": username}
        return {"access_token": create_jwt_token(token_data), "token_type": "bearer"}

#admin
@app.get("/admin", dependencies=[Depends(get_current_user)])
async def admin_route(current_user: user):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
    return {"message": "Admin route"}

#moder
@app.get("/moderator", dependencies=[Depends(get_current_user)])
async def moderator_route(current_user: user):
    if current_user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="Access denied. Moderator role required.")
    return {"message": "Moderator route"}

#other_users
@app.get("/user", dependencies=[Depends(get_current_user)])
async def user_route(current_user: user):
    return {"message": "User route"}