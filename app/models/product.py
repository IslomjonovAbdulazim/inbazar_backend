from sqlalchemy import Column, String, DateTime, Integer, Boolean, DECIMAL, ARRAY, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    unisex = "unisex"


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)

    # Product details
    sizes = Column(ARRAY(String), default=list)
    images = Column(ARRAY(String), default=list)
    colors = Column(ARRAY(String), default=list)
    tags = Column(ARRAY(String), default=list)

    # Stats
    click_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    category = relationship("Category")