# 🍫 See's Candies BI Assistant — Mockup POC

A conversational Business Intelligence assistant built with Streamlit + OpenAI GPT-4o + SQLite. Ask plain-English questions about See's Candies sales, production, and ecommerce data and get instant answers with auto-generated charts.

> **Mockup Demo — Not a final production tool.** Built by Karthik · March 2026

---

## Features

- 💬 **Natural language → SQL → plain English answer** via GPT-4o
- 📊 **Auto-generated charts** (bar, line, scatter, metric) via Plotly
- 🍫 **Pre-built mock data** — See's Candies themed SQLite database (490 rows)
- 💡 **8 sample questions** with pre-baked answers (no API key needed)
- 📋 **Schema viewer**, **SQL transparency**, and **raw data table**
- 🛠️ **"How is this built?"** section on the main page

---

## Tech Stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| Language Model | OpenAI GPT-4o |
| Database | SQLite (POC) |
| Charts | Plotly Express |
| Data | Pandas |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/koushik2299/Sees_candies.git
cd Sees_candies

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 4. Seed the database
python seed_data.py

# 5. Run the app
streamlit run app.py
```

> **Note:** The 8 suggested questions work without an API key using pre-built SQL queries and answer templates. A key is only needed for custom free-form questions.

---

## Project Structure

```
conversational_bi/
├── app.py            # Main Streamlit app
├── database.py       # SQLite connection (swappable to PostgreSQL/Snowflake)
├── llm.py            # GPT-4o text-to-SQL + answer generation
├── charts.py         # Auto chart type selection and rendering
├── schema.py         # Schema extractor for LLM prompt injection
├── seed_data.py      # Seeds SQLite with See's Candies mock data
├── requirements.txt
└── .env.example      # API key template
```

---

## Mock Data Tables

| Table | Rows | Description |
|---|---|---|
| `sales` | 220 | 10 stores across CA, NV, WA · 4 seasons |
| `production` | 110 | 4 production lines with defect tracking |
| `ecommerce_orders` | 160 | Online orders with return flags |

---

## Production Roadmap

To go from this POC to production:
- Connect a **real data warehouse** (Snowflake / BigQuery)
- Add **authentication** (SSO / LDAP)
- Add **query caching** and rate limiting
- Deploy on **cloud infrastructure** (GCP / AWS)
