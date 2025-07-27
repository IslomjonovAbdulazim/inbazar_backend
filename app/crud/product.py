from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
from uuid import UUID
from app.models.product import Product, GenderEnum
from app.schemas.product import ProductCreate, ProductUpdate


def get_product_by_id(db: Session, product_id: UUID, include_category: bool = False) -> Optional[Product]:
    query = db.query(Product)
    if include_category:
        query = query.options(joinedload(Product.category))
    return query.filter(Product.id == product_id).first()


def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        gender: Optional[GenderEnum] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        include_inactive: bool = False
) -> List[Product]:
    query = db.query(Product)

    if not include_inactive:
        query = query.filter(Product.is_active == True)

    if gender:
        query = query.filter(or_(Product.gender == gender, Product.gender == GenderEnum.unisex))

    if category_id:
        query = query.filter(Product.category_id == category_id)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_filter),
                Product.description.ilike(search_filter),
                Product.tags.any(search_filter)
            )
        )

    return query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()


def get_products_by_ids(db: Session, product_ids: List[UUID]) -> List[Product]:
    return db.query(Product).filter(Product.id.in_(product_ids)).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: UUID, product_update: ProductUpdate) -> Optional[Product]:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        for field, value in product_update.dict(exclude_unset=True).items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: UUID) -> bool:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


def increment_click_count(db: Session, product_id: UUID) -> None:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db_product.click_count += 1
        db.commit()


def increment_like_count(db: Session, product_id: UUID) -> None:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db_product.like_count += 1
        db.commit()


def decrement_like_count(db: Session, product_id: UUID) -> None:
    db_product = get_product_by_id(db, product_id)
    if db_product and db_product.like_count > 0:
        db_product.like_count -= 1
        db.commit()


def increment_bookmark_count(db: Session, product_id: UUID) -> None:
    db_product = get_product_by_id(db, product_id)
    if db_product:
        db_product.bookmark_count += 1
        db.commit()


def decrement_bookmark_count(db: Session, product_id: UUID) -> None:
    db_product = get_product_by_id(db, product_id)
    if db_product and db_product.bookmark_count > 0:
        db_product.bookmark_count -= 1
        db.commit()