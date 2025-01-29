from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_

from app.auth_utils import create_access_token, create_refresh_token, decode_access_token
from app.schemas import UserCreate, LogInModel
from app.database import Session, get_db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_router = APIRouter(
    prefix='/auth'
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@auth_router.post('/login/')
async def new_access_token_chat(user: LogInModel, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        or_(
            User.username == user.username_or_email,
            User.email == user.username_or_email
        )
    ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = create_access_token(db_user.id)
        refresh_token = create_refresh_token(db_user.id)

        token = {
            "access": access_token,
            "refresh": refresh_token
        }

        res = {
            "ok": True,
            "message": "User successfully login",
            "data": token
        }

        return res

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User or Password incorrect!")


@auth_router.post('/register/')
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='user with this username already exists!'
        )

    db_email = db.query(User).filter(User.email == user.email).first()

    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='user with this email already exists!'
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    db.add(new_user)
    db.commit()

    res = {
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email,
        'is_staff': new_user.is_staff,
        'is_active': new_user.is_active
    }
    return res


@auth_router.get('/me/')
async def auth_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    db_user = db.query(User).filter(User.id == payload.get('user_id')).first()
    res = {
        "username": db_user.username,
        "email": db_user.email
    }
    return {"message": res}
