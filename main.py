import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.utilities import SQLDatabase
from openai import OpenAI

from prompts.sql_chain import create_custom_sql_chain  # ✅ custom SQL chain
from qb import get_profit_and_loss, summarize_financials

# Load env vars
load_dotenv()

# Extract env vars once at runtime
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
qb_access_token = os.getenv("QB_ACCESS_TOKEN")

# OpenAI client for financial summaries
client = OpenAI(api_key=openai_api_key)


def ask_gpt_about_financials(financial_summary):
    prompt = f"""Here is a profit & loss summary:
{financial_summary}

Can you explain the business performance in plain English as if you're a CFO briefing a founder?"""

    response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {
                "role": "system",
                "content": "You are a CFO who explains financials clearly and concisely.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


# ──────────────────────────────────────────────────────────────
# LangChain SQL FastAPI App
# ──────────────────────────────────────────────────────────────

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Custom chain using only allowed tables + examples
db_path = "duckdb_finance.duckdb"
db = SQLDatabase.from_uri(f"duckdb:///{db_path}")
chain = create_custom_sql_chain(openai_model=openai_model, db_path=db_path)


@app.get("/query")
def query_endpoint(
    request: Request, query: str = None
):  # renamed function and param to avoid collision
    if query is None:
        return {"error": "Missing required query parameter: query"}

    try:
        response = chain.invoke({"query": query})  # match input key for chain
        raw_sql = response["intermediate_steps"][0]

        print("\n🔍 RAW SQL FROM CHAIN:\n", raw_sql)

        result = db.run(raw_sql)

        return {
            "query": query,
            "generated_sql": raw_sql,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


# ──────────────────────────────────────────────────────────────
# CLI fallback if run directly (prints GPT summary of P&L)
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    realm_id = "9341454982920695"

    report = get_profit_and_loss(realm_id, qb_access_token)
    print("\n📄 Raw P&L Report:")
    print(report)

    summary = summarize_financials(report)
    print("\n🧾 Summarized P&L:")
    print(summary)

    explanation = ask_gpt_about_financials(summary)
    print("\n📊 GPT Explanation of Profit & Loss:")
    print(explanation)
