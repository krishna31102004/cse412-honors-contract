from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from faker import Faker

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

TOTALS = {
    "users": 10_000,
    "categories": 25,
    "products": 20_000,
    "orders": 40_000,
    "order_items": 160_000,
}

STATUS_CHOICES = ["pending", "paid", "shipped", "delivered", "cancelled"]
STATUS_WEIGHTS = [0.05, 0.35, 0.25, 0.30, 0.05]

RANDOM_SEED = 20240320
UTC = timezone.utc
REFERENCE_NOW = datetime(2024, 3, 20, tzinfo=UTC)


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def random_price() -> Decimal:
    raw = Decimal(str(random.uniform(5, 500)))
    return quantize_money(raw)


def random_timestamp(days_back: int, reference: datetime | None = None) -> datetime:
    base = reference or REFERENCE_NOW
    start = base - timedelta(days=days_back)
    delta_seconds = (base - start).total_seconds()
    offset = random.random() * delta_seconds
    return start + timedelta(seconds=offset)


def write_csv(path: Path, headers: list[str], rows):
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def generate_users(fake: Faker):
    def rows():
        for _ in range(TOTALS["users"]):
            created_at = random_timestamp(365)
            yield [
                fake.name(),
                fake.unique.email(),
                created_at.isoformat(),
            ]

    fake.unique.clear()
    write_csv(DATA_DIR / "users.csv", ["full_name", "email", "created_at"], rows())


def generate_categories():
    category_names = [
        "Electronics",
        "Home & Kitchen",
        "Sports & Outdoors",
        "Books",
        "Toys & Games",
        "Beauty",
        "Health",
        "Automotive",
        "Clothing",
        "Shoes",
        "Jewelry",
        "Office",
        "Pet Supplies",
        "Garden",
        "Tools",
        "Music",
        "Movies",
        "Grocery",
        "Baby",
        "Art",
        "Furniture",
        "Crafts",
        "Video Games",
        "Appliances",
        "Smart Home",
    ]

    if len(category_names) != TOTALS["categories"]:
        raise ValueError("Category list must match configured total")

    rows = ([name] for name in category_names)
    write_csv(DATA_DIR / "categories.csv", ["name"], rows)


def generate_products(fake: Faker) -> list[Decimal]:
    product_prices: list[Decimal] = [Decimal("0.00")]

    def rows():
        for idx in range(1, TOTALS["products"] + 1):
            category_id = random.randint(1, TOTALS["categories"])
            price = random_price()
            product_prices.append(price)
            created_at = random_timestamp(365)
            name = f"{fake.color_name()} {fake.word().title()} {idx}"
            sku = f"SKU{idx:08d}"
            in_stock = random.randint(0, 1_000)
            yield [
                category_id,
                name,
                sku,
                f"{price:.2f}",
                in_stock,
                created_at.isoformat(),
            ]

    write_csv(
        DATA_DIR / "products.csv",
        ["category_id", "name", "sku", "price", "in_stock", "created_at"],
        rows(),
    )
    return product_prices


def generate_orders():
    def rows():
        for idx in range(1, TOTALS["orders"] + 1):
            user_id = random.randint(1, TOTALS["users"])
            order_date = random_timestamp(180)
            status = random.choices(STATUS_CHOICES, weights=STATUS_WEIGHTS, k=1)[0]
            yield [
                user_id,
                order_date.isoformat(),
                status,
            ]

    write_csv(
        DATA_DIR / "orders.csv",
        ["user_id", "order_date", "status"],
        rows(),
    )


def generate_order_items(product_prices: list[Decimal]):
    if len(product_prices) != TOTALS["products"] + 1:
        raise ValueError("Product price list missing entries")
    expected_items = TOTALS["orders"] * 4
    if expected_items != TOTALS["order_items"]:
        raise ValueError("order_items total must equal orders * 4")

    def rows():
        product_ids = list(range(1, TOTALS["products"] + 1))
        for order_id in range(1, TOTALS["orders"] + 1):
            for product_id in random.sample(product_ids, 4):
                qty = random.randint(1, 5)
                unit_price = product_prices[product_id]
                yield [
                    order_id,
                    product_id,
                    qty,
                    f"{unit_price:.2f}",
                ]

    write_csv(
        DATA_DIR / "order_items.csv",
        ["order_id", "product_id", "quantity", "unit_price"],
        rows(),
    )


def main():
    random.seed(RANDOM_SEED)
    fake = Faker()
    Faker.seed(RANDOM_SEED)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    generate_users(fake)
    generate_categories()
    product_prices = generate_products(fake)
    generate_orders()
    generate_order_items(product_prices)
    print("CSV files generated in", DATA_DIR)


if __name__ == "__main__":
    main()
