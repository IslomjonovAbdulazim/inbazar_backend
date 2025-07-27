from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.product import ProductResponse, ProductListResponse
from app.crud import product as product_crud, user as user_crud
from app.models.product import GenderEnum
from app.models.user import User

router = APIRouter()


@router.get("", response_model=List[ProductListResponse])
def get_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        gender: Optional[GenderEnum] = None,
        category_id: Optional[UUID] = None,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get products with filtering"""
    products = product_crud.get_products(
        db=db,
        skip=skip,
        limit=limit,
        gender=gender,
        category_id=category_id,
        search=search,
        include_inactive=False
    )

    return [
        ProductListResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            images=product.images,
            gender=product.gender
        )
        for product in products
    ]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
        product_id: UUID,
        db: Session = Depends(get_db)
):
    """Get product details"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not available"
        )

    return product


@router.post("/{product_id}/click")
def track_product_click(
        product_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Track product click"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Add to user's click history
    user_crud.add_to_click_history(db, current_user.id, product_id)

    # Increment product click count
    product_crud.increment_click_count(db, product_id)

    return {"message": "Click tracked successfully"}


@router.post("/{product_id}/like")
def like_product(
        product_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Like a product"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Add to user's liked products
    success = user_crud.add_to_liked_products(db, current_user.id, product_id)
    if success:
        # Increment product like count
        product_crud.increment_like_count(db, product_id)
        return {"message": "Product liked successfully"}
    else:
        return {"message": "Product already liked"}


@router.delete("/{product_id}/like")
def unlike_product(
        product_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Unlike a product"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Remove from user's liked products
    success = user_crud.remove_from_liked_products(db, current_user.id, product_id)
    if success:
        # Decrement product like count
        product_crud.decrement_like_count(db, product_id)
        return {"message": "Product unliked successfully"}
    else:
        return {"message": "Product was not liked"}


@router.post("/{product_id}/bookmark")
def bookmark_product(
        product_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Bookmark a product"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Add to user's bookmarked products
    success = user_crud.add_to_bookmarked_products(db, current_user.id, product_id)
    if success:
        # Increment product bookmark count
        product_crud.increment_bookmark_count(db, product_id)
        return {"message": "Product bookmarked successfully"}
    else:
        return {"message": "Product already bookmarked"}


@router.delete("/{product_id}/bookmark")
def remove_bookmark(
        product_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Remove bookmark from a product"""
    product = product_crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Remove from user's bookmarked products
    success = user_crud.remove_from_bookmarked_products(db, current_user.id, product_id)
    if success:
        # Decrement product bookmark count
        product_crud.decrement_bookmark_count(db, product_id)
        return {"message": "Bookmark removed successfully"}
    else:
        return {"message": "Product was not bookmarked"}