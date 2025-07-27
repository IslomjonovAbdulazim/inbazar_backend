from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    full_name: str


class UserCreate(UserBase):
    telegram_id: str
    phone_number: str
    telegram_username: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: str


class UserResponse(UserBase):
    id: UUID
    telegram_id: str
    phone_number: str
    telegram_username: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserInteractionsResponse(BaseModel):
    liked_products: List[UUID] = []
    bookmarked_products: List[UUID] = []
    click_history: List[UUID] = []

    class Config:
        from_attributes = True