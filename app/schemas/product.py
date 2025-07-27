from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from app.models.product import GenderEnum


class ProductBase(BaseModel):
    name: str
    description: str
    category_id: UUID
    gender: GenderEnum
    price: Decimal
    sizes: List[str] = []
    images: List[str] = []
    colors: List[str] = []
    tags: List[str] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    click_count: int
    like_count: int
    bookmark_count: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    id: UUID
    name: str
    price: Decimal
    images: List[str]
    gender: GenderEnum

    class Config:
        from_attributes = True


class ProductAdminResponse(ProductResponse):
    category_name: Optional[str] = None

    class Config:
        from_attributes = True