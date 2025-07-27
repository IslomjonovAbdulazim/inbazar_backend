from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_active_user
from app.schemas.user import UserResponse, UserUpdate, UserInteractionsResponse
from app.schemas.product import ProductListResponse
from app.crud import user as user_crud, product as product_crud
from app.models.user import User

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_my_profile(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Update current user profile"""
    updated_user = user_crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update profile"
        )
    return updated_user


@router.get("/me/likes", response_model=List[ProductListResponse])
def get_my_liked_products(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's liked products"""
    if not current_user.liked_products:
        return []

    products = product_crud.get_products_by_ids(db, current_user.liked_products)
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


@router.get("/me/bookmarks", response_model=List[ProductListResponse])
def get_my_bookmarked_products(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's bookmarked products"""
    if not current_user.bookmarked_products:
        return []

    products = product_crud.get_products_by_ids(db, current_user.bookmarked_products)
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


@router.get("/me/recent-clicks", response_model=List[ProductListResponse])
def get_my_recent_clicks(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get user's recent clicked products"""
    if not current_user.click_history:
        return []

    # Get first 10 recent clicks
    recent_ids = current_user.click_history[:10]
    products = product_crud.get_products_by_ids(db, recent_ids)

    # Sort by click history order
    products_dict = {product.id: product for product in products}
    ordered_products = [products_dict[pid] for pid in recent_ids if pid in products_dict]

    return [
        ProductListResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            images=product.images,
            gender=product.gender
        )
        for product in ordered_products
    ]