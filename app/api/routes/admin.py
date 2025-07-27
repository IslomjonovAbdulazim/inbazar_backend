from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.api.deps import get_current_admin_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductAdminResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import product as product_crud, category as category_crud
from app.models.user import User

router = APIRouter()


# Product Management
@router.post("/products", response_model=ProductAdminResponse)
def create_product(
        product: ProductCreate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Create a new product"""
    # Verify category exists
    category = category_crud.get_category_by_id(db, product.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )

    db_product = product_crud.create_product(db, product)
    response = ProductAdminResponse.from_orm(db_product)
    response.category_name = category.name
    return response


@router.get("/products", response_model=List[ProductAdminResponse])
def get_all_products(
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Get all products (including inactive)"""
    products = product_crud.get_products(db, include_inactive=True, limit=1000)

    # Get category names
    category_ids = list(set(product.category_id for product in products))
    categories = {cat.id: cat.name for cat in category_crud.get_categories(db)}

    result = []
    for product in products:
        response = ProductAdminResponse.from_orm(product)
        response.category_name = categories.get(product.category_id)
        result.append(response)

    return result


@router.get("/products/{product_id}", response_model=ProductAdminResponse)
def get_product_details(
        product_id: UUID,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Get product details with stats"""
    product = product_crud.get_product_by_id(db, product_id, include_category=True)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    response = ProductAdminResponse.from_orm(product)
    if product.category:
        response.category_name = product.category.name

    return response


@router.put("/products/{product_id}", response_model=ProductAdminResponse)
def update_product(
        product_id: UUID,
        product_update: ProductUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Update a product"""
    # Verify category exists if being updated
    if product_update.category_id:
        category = category_crud.get_category_by_id(db, product_update.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )

    updated_product = product_crud.update_product(db, product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Get category name
    category = category_crud.get_category_by_id(db, updated_product.category_id)
    response = ProductAdminResponse.from_orm(updated_product)
    if category:
        response.category_name = category.name

    return response


@router.delete("/products/{product_id}")
def delete_product(
        product_id: UUID,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Delete a product"""
    success = product_crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return {"message": "Product deleted successfully"}


# Category Management
@router.post("/categories", response_model=CategoryResponse)
def create_category(
        category: CategoryCreate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Create a new category"""
    # Check if category already exists
    existing = category_crud.get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    return category_crud.create_category(db, category)


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
        category_id: UUID,
        category_update: CategoryUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Update a category"""
    # Check if new name already exists
    if category_update.name:
        existing = category_crud.get_category_by_name(db, category_update.name)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )

    updated_category = category_crud.update_category(db, category_id, category_update)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return updated_category


@router.delete("/categories/{category_id}")
def delete_category(
        category_id: UUID,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Delete a category"""
    success = category_crud.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return {"message": "Category deleted successfully"}


# Analytics
@router.get("/analytics")
def get_analytics(
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Get basic analytics"""
    from sqlalchemy import func
    from app.models.user import User
    from app.models.product import Product
    from app.models.category import Category

    # Basic counts
    total_users = db.query(func.count(User.id)).scalar()
    total_products = db.query(func.count(Product.id)).scalar()
    active_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()
    total_categories = db.query(func.count(Category.id)).scalar()

    # Product stats
    total_clicks = db.query(func.sum(Product.click_count)).scalar() or 0
    total_likes = db.query(func.sum(Product.like_count)).scalar() or 0
    total_bookmarks = db.query(func.sum(Product.bookmark_count)).scalar() or 0

    return {
        "total_users": total_users,
        "total_products": total_products,
        "active_products": active_products,
        "total_categories": total_categories,
        "total_clicks": total_clicks,
        "total_likes": total_likes,
        "total_bookmarks": total_bookmarks
    }