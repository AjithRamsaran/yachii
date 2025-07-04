from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate


class ProductCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        db_product = Product(**product_data.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get(self, product_id: int) -> Optional[Product]:
        """Get a product by ID"""
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get a product by SKU"""
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        product_type: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_available: Optional[bool] = None,
        search: Optional[str] = None,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get multiple products with filtering and pagination"""
        query = self.db.query(Product)

        # Apply filters
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        if product_type:
            query = query.filter(Product.product_type.ilike(f"%{product_type}%"))
        
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if is_available is not None:
            query = query.filter(Product.is_available == is_available)
        
        if platform:
            query = query.filter(
                func.json_extract_path_text(Product.platforms, platform).isnot(None)
            )
        
        if search:
            search_filter = or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Get total count
        total = query.count()

        # Apply pagination
        products = query.offset(skip).limit(limit).all()

        return {
            "products": products,
            "total": total,
            "page": (skip // limit) + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }

    def update(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Update a product"""
        db_product = self.get(product_id)
        if not db_product:
            return None

        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: int) -> bool:
        """Delete a product"""
        db_product = self.get(product_id)
        if not db_product:
            return False

        self.db.delete(db_product)
        self.db.commit()
        return True

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        categories = self.db.query(Product.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]

    def get_brands(self) -> List[str]:
        """Get all unique brands"""
        brands = self.db.query(Product.brand).distinct().all()
        return [brand[0] for brand in brands if brand[0]]

    def get_product_types(self) -> List[str]:
        """Get all unique product types"""
        types = self.db.query(Product.product_type).distinct().all()
        return [ptype[0] for ptype in types if ptype[0]]

    def update_stock(self, product_id: int, quantity: int) -> Optional[Product]:
        """Update product stock quantity"""
        db_product = self.get(product_id)
        if not db_product:
            return None

        setattr(db_product, "stock_quantity", quantity)
        setattr(db_product, "is_available", quantity > 0)

        self.db.commit()
        self.db.refresh(db_product)
        return db_product