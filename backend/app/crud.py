from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import Select, and_, func, or_, select, text
from sqlalchemy.orm import Session, selectinload

from . import models, schemas


def list_users(db: Session, limit: int, offset: int) -> tuple[int, list[models.User]]:
    total = db.scalar(select(func.count()).select_from(models.User)) or 0
    stmt = select(models.User).order_by(models.User.id).offset(offset).limit(limit)
    users = db.execute(stmt).scalars().all()
    return total, users


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.get(models.User, user_id)


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(full_name=payload.full_name, email=payload.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_categories(db: Session) -> list[models.Category]:
    stmt = select(models.Category).order_by(models.Category.name)
    return db.execute(stmt).scalars().all()


def create_category(db: Session, payload: schemas.CategoryCreate) -> models.Category:
    category = models.Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_products(
    db: Session,
    limit: int,
    offset: int,
    *,
    category_id: int | None = None,
    query: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> tuple[int, list[models.Product]]:
    filters = []
    if category_id is not None:
        filters.append(models.Product.category_id == category_id)
    if query:
        pattern = f"%{query}%"
        filters.append(
            or_(
                models.Product.name.ilike(pattern),
                models.Product.sku.ilike(pattern),
            )
        )
    if min_price is not None:
        filters.append(models.Product.price >= min_price)
    if max_price is not None:
        filters.append(models.Product.price <= max_price)

    count_stmt: Select = select(func.count()).select_from(models.Product)
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total = db.scalar(count_stmt) or 0

    stmt = select(models.Product)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(models.Product.id).offset(offset).limit(limit)
    products = db.execute(stmt).scalars().all()
    return total, products


def get_product(db: Session, product_id: int) -> models.Product | None:
    return db.get(models.Product, product_id)


def create_product(db: Session, payload: schemas.ProductCreate) -> models.Product:
    product = models.Product(
        category_id=payload.category_id,
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        in_stock=payload.in_stock,
        created_at=datetime.now(timezone.utc),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_orders(
    db: Session,
    limit: int,
    offset: int,
    *,
    user_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> tuple[int, list[models.Order]]:
    filters = []
    if user_id is not None:
        filters.append(models.Order.user_id == user_id)
    if start_date is not None:
        filters.append(models.Order.order_date >= start_date)
    if end_date is not None:
        filters.append(models.Order.order_date <= end_date)

    count_stmt = select(func.count()).select_from(models.Order)
    if filters:
        count_stmt = count_stmt.where(and_(*filters))
    total = db.scalar(count_stmt) or 0

    stmt = select(models.Order)
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(models.Order.order_date.desc())
    stmt = stmt.offset(offset).limit(limit)
    orders = db.execute(stmt).scalars().all()
    return total, orders


def get_order_with_items(db: Session, order_id: int) -> models.Order | None:
    stmt = (
        select(models.Order)
        .options(selectinload(models.Order.items).selectinload(models.OrderItem.product))
        .where(models.Order.id == order_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def create_order(db: Session, payload: schemas.OrderCreate) -> models.Order:
    if not payload.items:
        raise ValueError("Order must contain at least one item")

    product_ids = [item.product_id for item in payload.items]
    if len(product_ids) != len(set(product_ids)):
        raise ValueError("Duplicate product_id in items")

    user = db.get(models.User, payload.user_id)
    if not user:
        raise LookupError("User not found")

    products = db.execute(
        select(models.Product).where(models.Product.id.in_(product_ids))
    ).scalars().all()
    product_map = {product.id: product for product in products}
    missing = set(product_ids) - set(product_map.keys())
    if missing:
        missing_str = ", ".join(str(mid) for mid in sorted(missing))
        raise LookupError(f"Products not found: {missing_str}")

    try:
        order = models.Order(
            user_id=payload.user_id,
            status=(payload.status or schemas.OrderStatus.pending).value,
            order_date=datetime.now(timezone.utc),
        )
        db.add(order)
        db.flush()

        for item in payload.items:
            product = product_map[item.product_id]
            if item.quantity <= 0:
                raise ValueError("Quantity must be greater than zero")
            if product.in_stock < item.quantity:
                raise ValueError(f"Insufficient stock for product {product.id}")
            product.in_stock -= item.quantity
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=product.price,
            )
            db.add(order_item)

        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def get_daily_sales(
    db: Session, *, start_date: date | None = None, end_date: date | None = None
) -> list[dict[str, object]]:
    clauses: list[str] = []
    params: dict[str, object] = {}
    if start_date is not None:
        clauses.append("sale_day::date >= :start_date")
        params["start_date"] = start_date
    if end_date is not None:
        clauses.append("sale_day::date <= :end_date")
        params["end_date"] = end_date

    where_sql = ""
    if clauses:
        where_sql = " WHERE " + " AND ".join(clauses)

    sql = text(
        "SELECT sale_day::date AS sale_day, total_sales "
        "FROM daily_sales_totals"
        + where_sql
        + " ORDER BY sale_day"
    )
    rows: list[dict[str, object]] = []
    for row in db.execute(sql, params):
        sale_day = row._mapping.get("sale_day")
        if isinstance(sale_day, datetime):
            sale_day = sale_day.date()
        rows.append(
            {
                "sale_day": sale_day,
                "total_sales": row._mapping.get("total_sales"),
            }
        )
    return rows
