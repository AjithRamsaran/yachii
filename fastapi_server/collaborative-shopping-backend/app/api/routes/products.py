from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from ...crud.product import ProductCRUD

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
    crud = ProductCRUD(db)
    
    # Check if SKU already exists
    if product.sku and crud.get_by_sku(product.sku):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    return crud.create(product)


@router.get("/", response_model=ProductListResponse)
def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of products to retrieve"),
    category: Optional[str] = Query(None, description="Filter by category"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    is_available: Optional[bool] = Query(None, description="Filter by availability"),
    search: Optional[str] = Query(None, description="Search in name, description, brand, category"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and pagination"""
    crud = ProductCRUD(db)
    result = crud.get_multi(
        skip=skip,
        limit=limit,
        category=category,
        product_type=product_type,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        is_available=is_available,
        search=search,
        platform=platform
    )
    return result


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    crud = ProductCRUD(db)
    product = crud.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product



@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    crud = ProductCRUD(db)
    
    # Check if SKU already exists for another product
    if product_update.sku:
        existing_product = crud.get_by_sku(product_update.sku)
        # if existing_product and existing_product.id != product_id: Todo
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Product with this SKU already exists"
        #     )
    
    updated_product = crud.update(product_id, product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    crud = ProductCRUD(db)
    success = crud.delete(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return None

