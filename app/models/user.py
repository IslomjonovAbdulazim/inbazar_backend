from sqlalchemy import Column, String, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    phone_number = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    telegram_username = Column(String, nullable=True)

    # User interactions
    liked_products = Column(ARRAY(UUID(as_uuid=True)), default=list)
    bookmarked_products = Column(ARRAY(UUID(as_uuid=True)), default=list)
    click_history = Column(ARRAY(UUID(as_uuid=True)), default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())