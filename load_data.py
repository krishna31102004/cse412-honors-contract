from __future__ import annotations

from pathlib import Path

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

COPY_TARGETS = [
    ("users", "users.csv", ["full_name", "email", "created_at"]),
    ("categories", "categories.csv", ["name"]),
    (
        "products",
        "products.csv",
        ["category_id", "name", "sku", "price", "in_stock", "created_at"],
    ),
    ("orders", "orders.csv", ["user_id", "order_date", "status"]),
    ("order_items", "order_items.csv", ["order_id", "product_id", "quantity", "unit_price"]),
]


def assert_data_files_exist() -> None:
    missing = [filename for _, filename, _ in COPY_TARGETS if not (DATA_DIR / filename).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing CSV files: {', '.join(missing)}. Run generate_data.py before load_data.py."
        )


def truncate_tables(conn: psycopg.Connection) -> None:
    query = "TRUNCATE TABLE order_items, orders, products, categories, users RESTART IDENTITY CASCADE;"
    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()


def copy_table(conn: psycopg.Connection, table: str, filename: str, columns: list[str]) -> None:
    path = DATA_DIR / filename
    print(f"Loading {table} from {path}")
    copy_sql = f"COPY {table} (" + ", ".join(columns) + ") FROM STDIN WITH (FORMAT csv, HEADER true)"
    with conn.cursor() as cur, path.open("r", encoding="utf-8") as data_file:
        with cur.copy(copy_sql) as copy:
            while True:
                chunk = data_file.read(1024 * 1024)
                if not chunk:
                    break
                copy.write(chunk)
    conn.commit()


def main() -> int:
    load_dotenv(dotenv_path=BASE_DIR / ".env")
    assert_data_files_exist()

    try:
        conn = psycopg.connect()
    except psycopg.OperationalError as exc:
        print(f"Failed to connect to PostgreSQL: {exc}")
        return 1

    with conn:
        truncate_tables(conn)
        for table, filename, columns in COPY_TARGETS:
            copy_table(conn, table, filename, columns)

    print("Data load complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
