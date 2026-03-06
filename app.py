"""
app.py
Main Streamlit application — See's Candies Conversational BI Assistant.
MOCKUP DEMO — Not a final production tool.
"""

import streamlit as st
import pandas as pd

from database import run_query
from schema import get_schema_string
from charts import render_chart

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="See's Candies BI Assistant (Mockup)",
    page_icon="🍫",
    layout="wide",
)

# ── Custom CSS — Light, readable palette ──────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAF8;
        color: #1E1E1E;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: #F5F0E8 !important;
        border-right: 1px solid #E0D6C8;
    }
    [data-testid="stSidebar"] * { color: #2C2416 !important; }
    [data-testid="stSidebar"] h2 { color: #7A1C1C !important; font-size: 1rem; }
    [data-testid="stSidebar"] .stExpander {
        border: 1px solid #D4B896 !important;
        border-radius: 8px;
        background: white;
    }

    /* ── Header banner ── */
    .bi-header {
        background: linear-gradient(135deg, #9B2335 0%, #C8841A 100%);
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        color: white;
        border: none;
    }
    .bi-header h1 {
        margin: 0 0 0.15rem;
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.3px;
        color: white;
    }
    .bi-header .sub {
        margin: 0;
        font-size: 0.95rem;
        color: rgba(255,255,255,0.88);
    }
    .mockup-badge {
        display: inline-block;
        background: rgba(255,255,255,0.25);
        border: 1px solid rgba(255,255,255,0.5);
        border-radius: 20px;
        padding: 0.15rem 0.7rem;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        color: white;
    }

    /* ── Answer box ── */
    .answer-box {
        background: #FFFFFF;
        border: 1px solid #E8D8C4;
        border-left: 4px solid #9B2335;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        font-size: 1.03rem;
        line-height: 1.65;
        color: #1E1E1E;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }

    /* ── Sample questions section ── */
    .questions-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #7A1C1C;
        margin: 1.2rem 0 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Input area ── */
    [data-testid="stTextInput"] input {
        border: 1.5px solid #D4B896;
        border-radius: 8px;
        background: #FFFFFF;
        padding: 0.6rem 0.9rem;
        font-size: 1rem;
        color: #1E1E1E;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: #9B2335;
        box-shadow: 0 0 0 2px rgba(155,35,53,0.12);
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"] {
        background: #9B2335 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        transition: background 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: #7A1C1C !important;
    }

    /* ── Secondary (sample question) buttons ── */
    .stButton > button:not([kind="primary"]) {
        background: #FFFFFF !important;
        color: #7A1C1C !important;
        border: 1.5px solid #D4B896 !important;
        border-radius: 20px !important;
        font-size: 0.82rem !important;
        padding: 0.3rem 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.15s !important;
        white-space: nowrap !important;
    }
    .stButton > button:not([kind="primary"]):hover {
        background: #FDF0E6 !important;
        border-color: #9B2335 !important;
        color: #9B2335 !important;
    }

    /* ── Metric card ── */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E8D8C4;
        border-top: 4px solid #9B2335;
        border-radius: 10px;
        padding: 1.25rem;
    }
    [data-testid="stMetric"] label { color: #6B5B4E !important; font-size: 0.85rem !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #9B2335 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }

    /* Expander headers */
    [data-testid="stExpander"] summary {
        color: #5A3820 !important;
        font-weight: 500;
    }

    /* Horizontal divider */
    hr { border-color: #E8D8C4; }

    /* History section */
    .history-q { font-weight: 600; color: #1E1E1E; }
    .history-a { color: #3D2B1F; }
</style>
""", unsafe_allow_html=True)

# ── Pre-baked mock answers (SQL + answer template) ─────────────────────────────
MOCK_QA = {
    "Which product category generates the most revenue?": {
        "sql": """
            SELECT category, ROUND(SUM(revenue), 2) AS total_revenue
            FROM sales GROUP BY category ORDER BY total_revenue DESC
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['category']}** leads all categories with **${df.iloc[0]['total_revenue']:,.0f}** in total revenue. "
            f"It's followed by {df.iloc[1]['category']} at ${df.iloc[1]['total_revenue']:,.0f} and "
            f"{df.iloc[2]['category']} at ${df.iloc[2]['total_revenue']:,.0f}."
            if len(df) >= 3 else f"**{df.iloc[0]['category']}** leads with **${df.iloc[0]['total_revenue']:,.0f}** in revenue."
        ),
    },
    "Which store had the highest sales?": {
        "sql": """
            SELECT store_name, region, ROUND(SUM(revenue), 2) AS total_revenue,
                   SUM(quantity_sold) AS total_units
            FROM sales GROUP BY store_name, region ORDER BY total_revenue DESC LIMIT 10
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['store_name']}** ({df.iloc[0]['region']}) had the highest sales, generating "
            f"**${df.iloc[0]['total_revenue']:,.0f}** in revenue across {df.iloc[0]['total_units']:,} units sold. "
            f"It outperformed {df.iloc[1]['store_name']} by ${df.iloc[0]['total_revenue'] - df.iloc[1]['total_revenue']:,.0f}."
            if len(df) >= 2 else f"**{df.iloc[0]['store_name']}** had the highest sales at ${df.iloc[0]['total_revenue']:,.0f}."
        ),
    },
    "What is the total revenue by season?": {
        "sql": """
            SELECT season, ROUND(SUM(revenue), 2) AS total_revenue,
                   COUNT(*) AS num_transactions
            FROM sales GROUP BY season ORDER BY total_revenue DESC
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['season']}** is the strongest season with **${df.iloc[0]['total_revenue']:,.0f}** in revenue "
            f"across {df.iloc[0]['num_transactions']} transactions. Regular-season sales come in at "
            f"${df[df['season']=='Regular']['total_revenue'].values[0]:,.0f} if available."
            if 'Regular' in df['season'].values else
            f"**{df.iloc[0]['season']}** leads with **${df.iloc[0]['total_revenue']:,.0f}** in total revenue."
        ),
    },
    "Which region is underperforming?": {
        "sql": """
            SELECT region, ROUND(SUM(revenue), 2) AS total_revenue,
                   ROUND(AVG(revenue), 2) AS avg_per_transaction,
                   COUNT(DISTINCT store_name) AS num_stores
            FROM sales GROUP BY region ORDER BY total_revenue ASC
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['region']}** is the lowest-performing region with **${df.iloc[0]['total_revenue']:,.0f}** "
            f"in total revenue across {df.iloc[0]['num_stores']} store(s). "
            f"Compared to the top region ({df.iloc[-1]['region']} at ${df.iloc[-1]['total_revenue']:,.0f}), "
            f"there is a gap of ${df.iloc[-1]['total_revenue'] - df.iloc[0]['total_revenue']:,.0f}."
        ),
    },
    "What is the defect rate by production line?": {
        "sql": """
            SELECT production_line,
                   SUM(units_produced) AS total_produced,
                   SUM(units_defective) AS total_defective,
                   ROUND(100.0 * SUM(units_defective) / SUM(units_produced), 2) AS defect_rate_pct
            FROM production GROUP BY production_line ORDER BY defect_rate_pct DESC
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['production_line']}** has the highest defect rate at "
            f"**{df.iloc[0]['defect_rate_pct']:.2f}%** ({df.iloc[0]['total_defective']:,} defective units from "
            f"{df.iloc[0]['total_produced']:,} produced). "
            f"{df.iloc[-1]['production_line']} performs best with a {df.iloc[-1]['defect_rate_pct']:.2f}% defect rate."
            if len(df) >= 2 else f"**{df.iloc[0]['production_line']}** has a {df.iloc[0]['defect_rate_pct']:.2f}% defect rate."
        ),
    },
    "Which ecommerce products have the highest return rate?": {
        "sql": """
            SELECT product_name, category,
                   COUNT(*) AS total_orders,
                   SUM(returned) AS total_returned,
                   ROUND(100.0 * SUM(returned) / COUNT(*), 1) AS return_rate_pct
            FROM ecommerce_orders GROUP BY product_name
            HAVING total_orders >= 3
            ORDER BY return_rate_pct DESC LIMIT 8
        """,
        "answer_fn": lambda df: (
            f"**{df.iloc[0]['product_name']}** has the highest return rate at "
            f"**{df.iloc[0]['return_rate_pct']:.1f}%** ({int(df.iloc[0]['total_returned'])} returns out of "
            f"{df.iloc[0]['total_orders']} orders). "
            f"{df.iloc[1]['product_name']} follows at {df.iloc[1]['return_rate_pct']:.1f}%."
            if len(df) >= 2 else f"**{df.iloc[0]['product_name']}** leads with a {df.iloc[0]['return_rate_pct']:.1f}% return rate."
        ),
    },
    "Compare Valentine's season revenue vs Christmas season revenue": {
        "sql": """
            SELECT season, ROUND(SUM(revenue), 2) AS total_revenue,
                   SUM(quantity_sold) AS total_units
            FROM sales WHERE season IN ('Valentine', 'Christmas')
            GROUP BY season ORDER BY total_revenue DESC
        """,
        "answer_fn": lambda df: (
            (lambda v, c: (
                f"**Christmas** outperforms Valentine's with **${c['total_revenue']:,.0f}** vs "
                f"**${v['total_revenue']:,.0f}** in revenue — a difference of ${c['total_revenue'] - v['total_revenue']:,.0f}. "
                f"Christmas also moved {c['total_units'] - v['total_units']:,} more units than Valentine's."
            ))(*[
                df[df['season']=='Valentine'].iloc[0] if 'Valentine' in df['season'].values else None,
                df[df['season']=='Christmas'].iloc[0] if 'Christmas' in df['season'].values else None
            ])
            if 'Valentine' in df['season'].values and 'Christmas' in df['season'].values
            else f"Seasonal data: {df.to_string(index=False)}"
        ),
    },
    "What are the top 5 best-selling products?": {
        "sql": """
            SELECT product_name, category,
                   SUM(quantity_sold) AS total_units,
                   ROUND(SUM(revenue), 2) AS total_revenue
            FROM sales GROUP BY product_name ORDER BY total_units DESC LIMIT 5
        """,
        "answer_fn": lambda df: (
            f"The top-selling product is **{df.iloc[0]['product_name']}** with "
            f"**{df.iloc[0]['total_units']:,} units** sold (${df.iloc[0]['total_revenue']:,.0f}). "
            f"The top 5 are: " +
            ", ".join(f"{row['product_name']} ({row['total_units']:,} units)" for _, row in df.iterrows())
            + "."
        ),
    },
}

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Sidebar (schema only) ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 About This Demo")
    st.info(
        "This is a **mockup prototype** using pre-built sample data. "
        "Click any suggested question below to see an example query and chart."
    )
    st.markdown("---")
    with st.expander("📋 View Database Schema", expanded=False):
        try:
            schema_text = get_schema_string()
            st.code(schema_text, language=None)
        except Exception as e:
            st.error(f"Could not load schema: {e}")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; padding: 0.5rem 0;'>"
        "<span style='font-size:0.78rem; color:#7A1C1C; font-weight:600;'>Built by Karthik</span><br>"
        "<span style='font-size:0.72rem; color:#9B7B6A;'>POC · March 2026</span>"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bi-header">
    <div class="mockup-badge">🚧 Mockup Demo — Not a Final Tool</div>
    <h1>🍫 See's Candies BI Assistant</h1>
    <p class="sub">Ask a question about sales, production, or ecommerce — powered by sample data.</p>
</div>
""", unsafe_allow_html=True)

# Input + Ask button
col_input, col_btn = st.columns([5, 1])
with col_input:
    user_question = st.text_input(
        label="question",
        placeholder="Type a question or click one below...",
        label_visibility="collapsed",
    )
with col_btn:
    submit = st.button("🔍 Ask", type="primary", use_container_width=True)

# Ask button clicked with typed question
if submit and user_question.strip():
    st.session_state["current_q"] = user_question.strip()
    st.rerun()
elif submit and not user_question.strip():
    st.warning("⚠️ Please type a question or click one of the suggested questions below.")

# Sample questions (below the input)
st.markdown('<p class="questions-label">💡 Suggested Questions — click any for instant results</p>', unsafe_allow_html=True)

q_list = list(MOCK_QA.keys())
cols = st.columns(2)
for i, q in enumerate(q_list):
    with cols[i % 2]:
        if st.button(q, key=f"sq_{i}"):
            st.session_state["current_q"] = q
            st.rerun()

st.markdown("---")


# ── Query execution ───────────────────────────────────────────────────────────
def run_mock_query(question: str):
    """Execute a pre-baked query for sample questions."""
    qa = MOCK_QA.get(question)
    if not qa:
        return None, None, None
    result = run_query(qa["sql"])
    if isinstance(result, str) or result is None or result.empty:
        return None, None, None
    try:
        answer_text = qa["answer_fn"](result)
    except Exception:
        answer_text = f"Here is the data for your question about '{question}'."
    return qa["sql"].strip(), result, answer_text


def show_results(question: str):
    """Run query and display answer, chart, SQL, and raw data."""
    import re
    with st.spinner("⏳ Fetching data..."):
        sql, df, answer = run_mock_query(question)

        if sql is None:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY", "")
            if api_key and api_key != "your_key_here":
                try:
                    from llm import generate_sql, generate_answer
                    from schema import get_schema_string
                    schema = get_schema_string()
                    sql = generate_sql(question, schema)
                    if sql.strip().upper() == "UNABLE_TO_ANSWER":
                        st.warning("⚠️ This question isn't in the dataset scope. Try one of the suggested questions.")
                        return
                    result = run_query(sql)
                    if isinstance(result, str) or result.empty:
                        st.warning("The query returned no results. Try rephrasing.")
                        return
                    df = result
                    answer = generate_answer(question, sql, df)
                except Exception as e:
                    st.error(f"Could not generate a response: {e}")
                    return
            else:
                st.info(
                    "💡 **Mockup demo.** Custom questions need an OpenAI key.\n\n"
                    "For a full demo, click one of the **Suggested Questions** above."
                )
                return

    if df is not None and not df.empty:
        st.session_state.history.append({"question": question, "answer": answer, "sql": sql})
        answer_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', answer)
        st.markdown(f'<div class="answer-box">💬 {answer_html}</div>', unsafe_allow_html=True)
        render_chart(df, question)
        with st.expander("🔧 View SQL Query", expanded=False):
            st.code(sql, language="sql")
        with st.expander("📊 View Raw Data", expanded=False):
            st.dataframe(df, use_container_width=True)


# ── Show results for current question ────────────────────────────────────────
current_q = st.session_state.get("current_q")
if current_q:
    show_results(current_q)

# ── Chat history ──────────────────────────────────────────────────────────────
if st.session_state.history:
    with st.expander(f"📜 Previous Questions ({len(st.session_state.history)})", expanded=False):
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"**Q:** {item['question']}")
            st.markdown(f"**A:** {item['answer']}")
            with st.expander("SQL", expanded=False):
                st.code(item["sql"], language="sql")
            st.markdown("---")

# ── How is this built? ────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("🛠️ How is this built?", expanded=False):
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("""
### Overview
A business user types a plain-English question and instantly receives:
- A **plain-English answer** summarizing the key insight
- An **auto-generated chart** tailored to the data shape
- The underlying **SQL query** and **raw data table** for transparency

No SQL skills required. The system translates natural language → SQL → insight automatically.

---

### How a query flows

1. 📝 **User asks a question** in plain English
2. 🧠 **GPT-4o reads the database schema** and writes a valid SQL query
3. 🗄️ **SQLite executes** the SQL and returns a results table
4. 💬 **GPT-4o reads the results** and writes a 2–3 sentence plain-English summary with real numbers
5. 📊 **Plotly auto-selects** the best chart type and renders it

---

### Why SQLite for the POC?
The database layer is fully swappable. Switching to **PostgreSQL, Snowflake, or BigQuery** only requires changing one connection function — all other logic stays identical.
        """)

    with col_b:
        st.markdown("""
### Tech Stack

| Layer | Tool |
|---|---|
| UI & App | Streamlit |
| Language Model | OpenAI GPT-4o |
| Database | SQLite (POC) |
| Charts | Plotly Express |
| Data Handling | Pandas |
| Language | Python 3.9+ |

---

### Mock Data
~490 rows of fictional See's Candies data across 3 tables:

| Table | Rows | Description |
|---|---|---|
| `sales` | 220 | 10 stores · CA, NV, WA · 4 seasons |
| `production` | 110 | 4 lines · defect rate tracking |
| `ecommerce_orders` | 160 | Online orders with returns |

Date range: **January 2023 – December 2024**

---

### Production Roadmap
To go from this POC to production:
- Connect a **real data warehouse** (Snowflake / BigQuery)
- Add **authentication** (SSO / LDAP)
- Add **query caching** and rate limiting
- Deploy on **cloud infrastructure** (GCP / AWS)
        """)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center; padding: 1.5rem 0 0.5rem; color:#9B7B6A; font-size:0.8rem;'>"
    "Built by <strong style='color:#7A1C1C;'>Karthik</strong> &nbsp;·&nbsp; POC · March 2026 &nbsp;·&nbsp; See's Candies BI Assistant"
    "</div>",
    unsafe_allow_html=True,
)

