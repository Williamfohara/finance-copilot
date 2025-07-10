import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from openai import OpenAI

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

# Enable CORS (if you’ll connect frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load LangChain tools
llm = ChatOpenAI(model=openai_model, temperature=0)
db = SQLDatabase.from_uri("duckdb:///duckdb_finance.duckdb")
chain = create_sql_query_chain(llm, db)


@app.get("/query")
def query(request: Request, question: str = None):
    """Return generated SQL and result for a finance question."""
    if question is None:
        return {"error": "Missing required query parameter: question"}

    try:
        sql = chain.invoke({"question": question})
        result = db.run(sql)
        return {"question": question, "generated_sql": sql, "result": result}
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
