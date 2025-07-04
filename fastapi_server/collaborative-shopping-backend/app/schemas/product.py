from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    product_type: str = Field(..., max_length=50)
    product_info: Optional[Dict[str, Any]] = None
    platforms: Optional[List[str]] = None
    stock_quantity: int = Field(default=0, ge=0)
    is_available: bool = True
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(default=0.0, ge=0, le=5)
    review_count: Optional[int] = Field(default=0, ge=0)

    @validator('original_price')
    def validate_original_price(cls, v, values):
        if v is not None and 'price' in values and v < values['price']:
            raise ValueError('Original price must be greater than or equal to current price')
        return v

    @validator('platforms')
    def validate_platforms(cls, v):
        if v is not None:
            valid_platforms = ['amazon', 'flipkart', 'myntra', 'ajio', 'nykaa', 'bigbasket', 'other']
            for platform in v:
                if platform.lower() not in valid_platforms:
                    # Allow custom platforms but convert to lowercase
                    pass
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    product_type: Optional[str] = Field(None, max_length=50)
    product_info: Optional[Dict[str, Any]] = None
    platforms: Optional[List[str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int