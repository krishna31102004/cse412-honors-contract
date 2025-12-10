from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .db import get_db

app = FastAPI(title="Order Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


LIMIT_QUERY = Query(25, ge=1, le=100)
OFFSET_QUERY = Query(0, ge=0)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/users", response_model=schemas.UserList)
def list_users(
    limit: int = LIMIT_QUERY,
    offset: int = OFFSET_QUERY,
    db: Session = Depends(get_db),
):
    total, users = crud.list_users(db, limit=limit, offset=offset)
    return {"items": users, "limit": limit, "offset": offset, "total": total}


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        user = crud.create_user(db, user_in)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")


@app.get("/categories", response_model=schemas.CategoryList)
def list_categories(db: Session = Depends(get_db)):
    categories = crud.list_categories(db)
    return {"items": categories}


@app.post("/categories", response_model=schemas.CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(category_in: schemas.CategoryCreate, db: Session = Depends(get_db)):
    try:
        category = crud.create_category(db, category_in)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category name already exists")


@app.get("/products", response_model=schemas.ProductList)
def list_products(
    limit: int = LIMIT_QUERY,
    offset: int = OFFSET_QUERY,
    category_id: Optional[int] = Query(None, ge=1),
    q: Optional[str] = Query(None, min_length=1),
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot exceed max_price")
    total, products = crud.list_products(
        db,
        limit=limit,
        offset=offset,
        category_id=category_id,
        query=q,
        min_price=min_price,
        max_price=max_price,
    )
    return {"items": products, "limit": limit, "offset": offset, "total": total}


@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.post("/products", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(product_in: schemas.ProductCreate, db: Session = Depends(get_db)):
    if not db.get(models.Category, product_in.category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    try:
        product = crud.create_product(db, product_in)
        return product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Product with same SKU already exists")


@app.get("/orders", response_model=schemas.OrderList)
def list_orders(
    limit: int = LIMIT_QUERY,
    offset: int = OFFSET_QUERY,
    user_id: Optional[int] = Query(None, ge=1),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")
    total, orders = crud.list_orders(
        db,
        limit=limit,
        offset=offset,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return {"items": orders, "limit": limit, "offset": offset, "total": total}


@app.get("/orders/{order_id}", response_model=schemas.OrderDetail)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.get_order_with_items(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.post("/orders", response_model=schemas.OrderDetail, status_code=status.HTTP_201_CREATED)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    try:
        order = crud.create_order(db, order_in)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    order_with_items = crud.get_order_with_items(db, order.id)
    if not order_with_items:
        raise HTTPException(status_code=500, detail="Failed to load created order")
    return order_with_items


@app.get("/analytics/daily-sales", response_model=schemas.AnalyticsResponse)
def daily_sales(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")
    rows = crud.get_daily_sales(db, start_date=start_date, end_date=end_date)
    points = [schemas.DailySalesPoint(**row) for row in rows]
    return {"items": points}
