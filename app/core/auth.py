from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.config import settings
from app.crud import user as user_crud
from app.models.user import User


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        telegram_id: str = payload.get("sub")
        if telegram_id is None:
            return None
        return telegram_id
    except JWTError:
        return None


def get_current_user(db: Session, token: str) -> Optional[User]:
    telegram_id = verify_token(token)
    if telegram_id is None:
        return None

    user = user_crud.get_user_by_telegram_id(db, telegram_id)
    return user


def is_admin(user: User) -> bool:
    return user.telegram_id == settings.admin_telegram_id