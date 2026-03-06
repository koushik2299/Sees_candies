"""
charts.py
Auto chart type selection and rendering using Plotly Express.
See's Candies brand colors: deep red #8B0000, warm gold #C9A84C.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BRAND_RED = "#8B0000"
BRAND_GOLD = "#C9A84C"
BRAND_PALETTE = [BRAND_RED, BRAND_GOLD, "#B5451B", "#E8C87A", "#6B0F0F", "#F0D9A0"]


def _has_date_column(df: pd.DataFrame) -> str | None:
    """Returns the name of the first date-like column, or None."""
    for col in df.columns:
        if any(kw in col.lower() for kw in ("date", "month", "year", "week", "day")):
            return col
    return None


def _get_numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def _get_non_numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude="number").columns.tolist()


def render_chart(df: pd.DataFrame, user_question: str):
    """
    Intelligently selects and renders a Plotly chart based on the DataFrame shape
    and question content. Displays using st.plotly_chart().
    """
    if df is None or df.empty:
        return

    numeric_cols = _get_numeric_cols(df)
    non_numeric_cols = _get_non_numeric_cols(df)
    date_col = _has_date_column(df)
    n_rows, n_cols = df.shape

    # Single numeric result → Big number metric
    if n_rows == 1 and len(numeric_cols) == 1:
        val = df[numeric_cols[0]].iloc[0]
        label = numeric_cols[0].replace("_", " ").title()
        formatted = f"${val:,.2f}" if "revenue" in numeric_cols[0].lower() else f"{val:,.0f}"
        st.metric(label=label, value=formatted)
        return

    # Date column present → Line chart
    if date_col and numeric_cols:
        value_col = numeric_cols[0]
        try:
            df_sorted = df.sort_values(date_col)
            fig = px.line(
                df_sorted,
                x=date_col,
                y=value_col,
                title=f"{value_col.replace('_', ' ').title()} over Time",
                color_discrete_sequence=[BRAND_RED],
                markers=True,
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#333",
            )
            st.plotly_chart(fig, use_container_width=True)
            return
        except Exception:
            pass

    # Two numeric columns → Scatter plot
    if len(numeric_cols) >= 2 and len(non_numeric_cols) == 0:
        fig = px.scatter(
            df,
            x=numeric_cols[0],
            y=numeric_cols[1],
            title=f"{numeric_cols[0].replace('_', ' ').title()} vs {numeric_cols[1].replace('_', ' ').title()}",
            color_discrete_sequence=[BRAND_RED],
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        return

    # One categorical + one numeric → Bar chart
    if non_numeric_cols and numeric_cols:
        cat_col = non_numeric_cols[0]
        val_col = numeric_cols[0]
        df_sorted = df.sort_values(val_col, ascending=False).head(20)
        fig = px.bar(
            df_sorted,
            x=cat_col,
            y=val_col,
            title=f"{val_col.replace('_', ' ').title()} by {cat_col.replace('_', ' ').title()}",
            color=val_col,
            color_continuous_scale=[[0, BRAND_GOLD], [1, BRAND_RED]],
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            xaxis_tickangle=-35,
        )
        st.plotly_chart(fig, use_container_width=True)
        return

    # Fallback: generic bar chart using first two columns
    if n_cols >= 2:
        fig = px.bar(
            df.head(20),
            x=df.columns[0],
            y=df.columns[1] if len(numeric_cols) > 0 else df.columns[1],
            title="Results",
            color_discrete_sequence=[BRAND_RED],
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
