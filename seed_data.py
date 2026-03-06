"""
seed_data.py
Run once to create and populate sees_candies.db with mock data.
Also called automatically by app.py on first startup (cloud-safe).
Usage: python seed_data.py
"""

import sqlite3
import random
from pathlib import Path
from datetime import date, timedelta

# Always resolve DB path relative to this file — safe on Streamlit Cloud
DB_PATH = Path(__file__).parent / "sees_candies.db"

STORES = [
    (1, "Beverly Hills", "Southern California"),
    (2, "San Francisco Union Square", "Northern California"),
    (3, "San Diego Gaslamp", "Southern California"),
    (4, "Sacramento Arden Fair", "Northern California"),
    (5, "Las Vegas Strip", "Nevada"),
    (6, "Reno Summit Sierra", "Nevada"),
    (7, "Seattle Pike Place", "Washington"),
    (8, "Bellevue Square", "Washington"),
    (9, "Los Angeles DTLA", "Southern California"),
    (10, "Pasadena Arroyo", "Southern California"),
]

PRODUCTS = [
    ("Dark Chocolate Nuts & Chews", "Nuts & Chews"),
    ("Milk Bordeaux", "Boxed Chocolates"),
    ("Victoria Toffee", "Boxed Chocolates"),
    ("Peanut Brittle", "Nuts & Chews"),
    ("Milk Chocolate Lollipop", "Lollipops"),
    ("Scotchmallow", "Boxed Chocolates"),
    ("California Brittle", "Nuts & Chews"),
    ("Dark Chocolate Truffle", "Truffles"),
    ("Milk Chocolate Truffle", "Truffles"),
    ("Butterscotch Square", "Boxed Chocolates"),
    ("Almond Royal", "Nuts & Chews"),
    ("Cherry Cream", "Boxed Chocolates"),
    ("Raspberry Cream", "Boxed Chocolates"),
    ("Strawberry Cream", "Boxed Chocolates"),
    ("Vanilla Lollipop", "Lollipops"),
    ("Chocolate Lollipop", "Lollipops"),
    ("Sea Salt Caramel Truffle", "Truffles"),
    ("Dark Truffle Assortment", "Truffles"),
]

PRODUCTION_LINES = ["Line A", "Line B", "Line C", "Line D"]

SEASON_WINDOWS = {
    "Valentine": [(date(2023, 1, 22), date(2023, 2, 14)), (date(2024, 1, 21), date(2024, 2, 14))],
    "Easter":    [(date(2023, 3, 15), date(2023, 4, 9)),  (date(2024, 3, 10), date(2024, 3, 31))],
    "Christmas": [(date(2023, 11, 20), date(2023, 12, 26)), (date(2024, 11, 18), date(2024, 12, 26))],
}

PRICE_MAP = {
    "Boxed Chocolates": (28.0, 55.0),
    "Lollipops": (8.0, 14.0),
    "Truffles": (18.0, 36.0),
    "Nuts & Chews": (16.0, 30.0),
}

SEASON_MULTIPLIER = {
    "Valentine": 1.4,
    "Easter": 1.2,
    "Christmas": 1.6,
    "Regular": 1.0,
}


def get_season(d: date) -> str:
    for season, windows in SEASON_WINDOWS.items():
        for start, end in windows:
            if start <= d <= end:
                return season
    return "Regular"


def random_date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        DROP TABLE IF EXISTS sales;
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY,
            date TEXT,
            store_id INTEGER,
            store_name TEXT,
            region TEXT,
            product_name TEXT,
            category TEXT,
            quantity_sold INTEGER,
            revenue REAL,
            season TEXT
        );

        DROP TABLE IF EXISTS production;
        CREATE TABLE production (
            id INTEGER PRIMARY KEY,
            date TEXT,
            product_name TEXT,
            category TEXT,
            units_produced INTEGER,
            units_defective INTEGER,
            production_line TEXT
        );

        DROP TABLE IF EXISTS ecommerce_orders;
        CREATE TABLE ecommerce_orders (
            id INTEGER PRIMARY KEY,
            date TEXT,
            product_name TEXT,
            category TEXT,
            quantity INTEGER,
            revenue REAL,
            returned INTEGER,
            customer_state TEXT
        );
    """)


def seed_sales(conn: sqlite3.Connection, n: int = 220):
    rows = []
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    for i in range(1, n + 1):
        d = random_date_in_range(start_date, end_date)
        store = random.choice(STORES)
        product, category = random.choice(PRODUCTS)
        season = get_season(d)
        qty = int(random.randint(2, 30) * SEASON_MULTIPLIER[season])
        lo, hi = PRICE_MAP[category]
        unit_price = round(random.uniform(lo, hi), 2)
        revenue = round(qty * unit_price, 2)
        rows.append((
            i, d.isoformat(), store[0], store[1], store[2],
            product, category, qty, revenue, season
        ))
    conn.executemany(
        "INSERT INTO sales VALUES (?,?,?,?,?,?,?,?,?,?)", rows
    )


def seed_production(conn: sqlite3.Connection, n: int = 110):
    rows = []
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    for i in range(1, n + 1):
        d = random_date_in_range(start_date, end_date)
        product, category = random.choice(PRODUCTS)
        line = random.choice(PRODUCTION_LINES)
        produced = random.randint(200, 1200)
        defect_rate = random.uniform(0.01, 0.08)
        defective = int(produced * defect_rate)
        rows.append((i, d.isoformat(), product, category, produced, defective, line))
    conn.executemany(
        "INSERT INTO production VALUES (?,?,?,?,?,?,?)", rows
    )


def seed_ecommerce(conn: sqlite3.Connection, n: int = 160):
    states = ["CA", "NV", "WA", "OR", "AZ", "TX", "NY", "FL", "CO", "IL"]
    rows = []
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    for i in range(1, n + 1):
        d = random_date_in_range(start_date, end_date)
        product, category = random.choice(PRODUCTS)
        qty = random.randint(1, 8)
        lo, hi = PRICE_MAP[category]
        unit_price = round(random.uniform(lo, hi), 2)
        revenue = round(qty * unit_price, 2)
        returned = 1 if random.random() < 0.12 else 0
        state = random.choice(states)
        rows.append((i, d.isoformat(), product, category, qty, revenue, returned, state))
    conn.executemany(
        "INSERT INTO ecommerce_orders VALUES (?,?,?,?,?,?,?,?)", rows
    )


def seed(conn: sqlite3.Connection):
    """Create tables and insert all mock data into the given connection."""
    random.seed(42)
    create_tables(conn)
    seed_sales(conn)
    seed_production(conn)
    seed_ecommerce(conn)
    conn.commit()


def auto_seed():
    """
    Called at app startup. Creates and seeds sees_candies.db if it doesn't
    already exist. Safe to call on every startup — no-op if DB is present.
    """
    if not DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        seed(conn)
        conn.close()


if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    seed(conn)
    conn.close()
    print(f"✅ Database created: {DB_PATH}")
    print("   Tables: sales (220 rows), production (110 rows), ecommerce_orders (160 rows)")
