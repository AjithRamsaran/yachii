from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from fastapi import status
from typing import List, Dict, Any
from pydantic import BaseModel
from typing import Optional
router = APIRouter()





class Product(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    product_type: str
    product_info: Optional[Any] = None
    platforms: Optional[List[str]] = None
    stock_quantity: Optional[int] = 0
    is_available: Optional[bool] = True
    images: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    sku: Optional[str] = None
    rating: Optional[float] = 0.0
    review_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    product: Product


class Order(BaseModel):
    id: Optional[int]
    items: List[CartItem]
    total_price: float
    
# In-memory cart and connections
cart: Dict[str, Any] = {"items": []}
active_connections: List[WebSocket] = []
orders: List[Order] = []
order_id_counter = 1

def get_cart():
    return cart

async def broadcast_cart():
    for connection in active_connections:
        await connection.send_json(cart)

# REST API endpoints

@router.get("/items", response_model=Dict[str, Any])
async def read_products():
    return get_cart()

@router.post("/items", status_code=status.HTTP_200_OK)
async def add_item(item: CartItem):
    for existing in cart["items"]:
        if existing["id"] == item.id:
            existing["quantity"] += item.quantity
            await broadcast_cart()
            return get_cart()
    cart["items"].append(item.model_dump())
    await broadcast_cart()
    return get_cart()

@router.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(item_id: int, item: CartItem):
    print(item)
    for existing in cart["items"]:
        if existing["id"] == item_id:
            existing["quantity"] = item.quantity
           # existing["name"] = item.name
           # existing["product"] = item.product.dict() if item.product else None
            await broadcast_cart()
            return get_cart()
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item(item_id: int):
    for i, existing in enumerate(cart["items"]):
        if existing["id"] == item_id:
            del cart["items"][i]
            await broadcast_cart()
            return get_cart()
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/placeorder", status_code=status.HTTP_201_CREATED)
async def place_order(order: Order):
    global order_id_counter
    if not order.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    order.id = order_id_counter  # Assign auto-incremented ID
    order_id_counter += 1
    orders.append(order)
    # Optionally, clear the cart after placing the order
    cart["items"].clear()
    await broadcast_cart()
    return {"message": "Order placed successfully", "order": order}

def get_orders():
    return orders

@router.get("/orders", response_model=Dict[str, Any])
async def read_orders():
    return {"orders" : get_orders()}

# WebSocket endpoint

@router.websocket("/ws/cart")
async def websocket_cart(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json(cart)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)