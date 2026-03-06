"""
schema.py
Extracts and formats the database schema for injecting into LLM prompts.
"""

import sqlite3
from database import get_connection


def get_schema_string() -> str:
    """
    Reads all table names and column definitions from the database.
    Returns a clean text block suitable for LLM context injection.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_defs = ", ".join(f"{col[1]} ({col[2]})" for col in columns)
        schema_parts.append(f"Table: {table}\nColumns: {col_defs}")

    conn.close()
    return "\n\n".join(schema_parts)
