from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status
import bcrypt
from ..models import Users
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=8, max_length=64)


class PhoneNumberRequest(BaseModel):
    phone_number: str


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed.')
    return db.query(Users).filter(Users.id == user['user_id']).first()


@router.put("/change_password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed.')

    user_model = db.query(Users).filter(Users.id == user['user_id']).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User does not exist.')
    if not bcrypt.checkpw(user_verification.password.encode('utf-8'),
                          user_model.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail='Authentication Failed.')

    user_model.hashed_password = bcrypt.hashpw(
        user_verification.new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    db.commit()


@router.put("/update_phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(user: user_dependency, db: db_dependency, phone_number_request: PhoneNumberRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed.')

    user_model = db.query(Users).filter(Users.id == user['user_id']).first()
    if not user_model:
        raise HTTPException(status_code=404, detail='User does not exist.')

    user_model.phone_number = phone_number_request.phone_number
    db.commit()
