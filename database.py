"""
database.py
Handles SQLite connection and query execution.
Designed to be swappable — replace `get_connection()` to use PostgreSQL or Snowflake.
"""
from __future__ import annotations

import sqlite3
import pandas as pd
from pathlib import Path
from typing import Union

DB_PATH = Path(__file__).parent / "sees_candies.db"


def get_connection() -> sqlite3.Connection:
    """
    Returns a database connection.
    To swap to PostgreSQL: replace with psycopg2.connect(...)
    To swap to Snowflake: replace with snowflake.connector.connect(...)
    """
    return sqlite3.connect(DB_PATH)


def run_query(sql: str) -> Union[pd.DataFrame, str]:
    """
    Executes a SQL string and returns a pandas DataFrame.
    Returns an error message string if the query fails.
    """
    try:
        conn = get_connection()
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        return f"Query error: {str(e)}"
