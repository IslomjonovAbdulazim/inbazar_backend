from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from uuid import UUID
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_telegram_id(db: Session, telegram_id: str) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def add_to_liked_products(db: Session, user_id: UUID, product_id: UUID) -> bool:
    db_user = get_user_by_id(db, user_id)
    if db_user and product_id not in (db_user.liked_products or []):
        liked = list(db_user.liked_products or [])
        liked.append(product_id)
        db_user.liked_products = liked
        db.commit()
        return True
    return False


def remove_from_liked_products(db: Session, user_id: UUID, product_id: UUID) -> bool:
    db_user = get_user_by_id(db, user_id)
    if db_user and product_id in (db_user.liked_products or []):
        liked = list(db_user.liked_products or [])
        liked.remove(product_id)
        db_user.liked_products = liked
        db.commit()
        return True
    return False


def add_to_bookmarked_products(db: Session, user_id: UUID, product_id: UUID) -> bool:
    db_user = get_user_by_id(db, user_id)
    if db_user and product_id not in (db_user.bookmarked_products or []):
        bookmarked = list(db_user.bookmarked_products or [])
        bookmarked.append(product_id)
        db_user.bookmarked_products = bookmarked
        db.commit()
        return True
    return False


def remove_from_bookmarked_products(db: Session, user_id: UUID, product_id: UUID) -> bool:
    db_user = get_user_by_id(db, user_id)
    if db_user and product_id in (db_user.bookmarked_products or []):
        bookmarked = list(db_user.bookmarked_products or [])
        bookmarked.remove(product_id)
        db_user.bookmarked_products = bookmarked
        db.commit()
        return True
    return False


def add_to_click_history(db: Session, user_id: UUID, product_id: UUID) -> None:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        history = list(db_user.click_history or [])
        # Remove if already exists to move to front
        if product_id in history:
            history.remove(product_id)
        # Add to front
        history.insert(0, product_id)
        # Keep only last 50 clicks
        history = history[:50]
        db_user.click_history = history
        db.commit()