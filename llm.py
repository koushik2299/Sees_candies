"""
llm.py
LLM integration — Text-to-SQL conversion and plain English answer generation
using OpenAI GPT-4o.
"""

import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_key_here":
            raise ValueError("OPENAI_API_KEY is not set in your .env file.")
        _client = OpenAI(api_key=api_key)
    return _client


def generate_sql(user_question: str, schema: str) -> str:
    """
    Converts a natural language question into a SQL query using GPT-4o.
    Returns the raw SQL string, or 'UNABLE_TO_ANSWER' if the question cannot be answered.
    """
    client = get_client()

    system_prompt = (
        "You are a SQL expert assistant for See's Candies, a chocolate manufacturer and retailer.\n"
        "You will be given a database schema and a user question.\n"
        "Your job is to write a valid SQLite SQL query that answers the question.\n"
        "Return ONLY the raw SQL query with no explanation, no markdown, no backticks.\n"
        "If the question cannot be answered from the schema, return the string: UNABLE_TO_ANSWER"
    )

    user_message = f"Schema:\n{schema}\n\nQuestion:\n{user_question}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0,
        max_tokens=512,
    )

    return response.choices[0].message.content.strip()


def generate_answer(user_question: str, sql: str, df: pd.DataFrame) -> str:
    """
    Generates a 2-3 sentence plain English answer summarizing the key insight
    from the query results.
    """
    client = get_client()

    system_prompt = (
        "You are a friendly business analytics assistant for See's Candies.\n"
        "You will be given a user question, the SQL query that was run, and the resulting data as a table.\n"
        "Write a clear 2-3 sentence plain English answer summarizing the key insight from the data.\n"
        "Be specific — reference actual numbers and product names from the data.\n"
        "Do not mention SQL or technical details."
    )

    user_message = (
        f"Question: {user_question}\n"
        f"SQL Run: {sql}\n"
        f"Data: {df.to_string(index=False)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()
