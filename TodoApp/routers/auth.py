import os
from copyreg import dispatch_table
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from dotenv import load_dotenv
from database import SessionLocal
from starlette import status
from models import Users
import bcrypt


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


router = APIRouter()

load_dotenv()
SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: db_dependency) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return user
    return None


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    payload = {'sub': username, 'id': user_id}
    expires = int((datetime.now(timezone.utc) + expires_delta).timestamp())
    payload.update({'exp': expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload['sub']
        user_id: int = payload['id']
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        return {'username': username, 'user_id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt.hashpw(
            create_user_request.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8'),
        is_active=True,
        role=create_user_request.role,
    )
    db.add(user)
    db.commit()


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    token = create_access_token(form_data.username, user.id, timedelta(minutes=30))
    return {'access_token': token, 'token_type': 'bearer'}
