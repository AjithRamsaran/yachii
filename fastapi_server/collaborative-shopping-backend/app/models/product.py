from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from ..core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    original_price = Column(Float)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    brand = Column(String(100), index=True)
    product_type = Column(String(50), nullable=False, index=True)
    product_info = Column(JSON)  
    platforms = Column(JSON)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    images = Column(JSON)  
    thumbnail = Column(String(500))  
    tags = Column(JSON)
    sku = Column(String(100), unique=True, index=True) 
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"