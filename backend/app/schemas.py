from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

try:
    from pydantic import BaseModel, ConfigDict, Field
except ImportError:
    from pydantic import BaseModel, Field

    ConfigDict = None


class ORMModel(BaseModel):
    if ConfigDict is not None:
        model_config = ConfigDict(from_attributes=True)
    else:
        class Config:
            orm_mode = True


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class UserCreate(BaseModel):
    full_name: str
    email: str


class UserOut(ORMModel):
    id: int
    full_name: str
    email: str
    created_at: datetime


class CategoryCreate(BaseModel):
    name: str


class CategoryOut(ORMModel):
    id: int
    name: str


class ProductCreate(BaseModel):
    category_id: int
    name: str
    sku: str = Field(..., pattern=r"^SKU\d{8}$")
    price: Decimal
    in_stock: int = Field(..., ge=0)


class ProductOut(ORMModel):
    id: int
    category_id: int
    name: str
    sku: str
    price: Decimal
    in_stock: int
    created_at: datetime


class Pagination(BaseModel):
    limit: int
    offset: int
    total: int


class UserList(Pagination):
    items: List[UserOut]


class ProductList(Pagination):
    items: List[ProductOut]


class OrderSummary(ORMModel):
    id: int
    user_id: int
    order_date: datetime
    status: OrderStatus


class OrderList(Pagination):
    items: List[OrderSummary]


class OrderItemInput(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    user_id: int
    status: Optional[OrderStatus] = OrderStatus.pending
    items: List[OrderItemInput]


class OrderItemDetail(ORMModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product_name: Optional[str]
    product_sku: Optional[str]


class OrderDetail(ORMModel):
    id: int
    user_id: int
    order_date: datetime
    status: OrderStatus
    items: List[OrderItemDetail]


class DailySalesPoint(BaseModel):
    sale_day: date
    total_sales: Decimal


class AnalyticsResponse(BaseModel):
    items: List[DailySalesPoint]


class CategoryList(BaseModel):
    items: List[CategoryOut]
