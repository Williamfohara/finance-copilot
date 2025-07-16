import os
import re
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import BaseModel

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
    prompt = f"""Here is a profit & loss summary: {financial_summary}

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


def explain_sql_results(question: str, sql_query: str, results: List[Dict[str, Any]]) -> str:
    try:
        results_text = ""
        if not results or (len(results) == 1 and "message" in results[0]):
            results_text = "No data was found for this query."
        else:
            for i, row in enumerate(results):
                if i < 10:
                    row_text = ", ".join([f"{k}: {v}" for k, v in row.items()])
                    results_text += f"Row {i+1}: {row_text}\n"
                elif i == 10:
                    results_text += f"... and {len(results)-10} more rows\n"
                    break

        prompt = f"""The user asked: \"{question}\"

The SQL query generated was: {sql_query}

The query returned the following data:
{results_text}

Please provide a clear, natural language explanation of what this data shows,
as if you're explaining it to a business owner who doesn't know SQL. Focus on the
key insights and what this means for their business.

If the data shows financial information like revenue, expenses, or profits,
explain the business implications. If it shows no data, explain what that means
and suggest what they might want to look for instead.

Keep the explanation conversational and actionable."""

        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful financial analyst who explains data in plain English. Be insightful, and focus on business implications.",
                },
                {"role": "user", "content": prompt},
            ],
            timeout=30,
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Error generating natural language explanation: {str(e)}")
        if not results:
            return f"I couldn't find any data for your question: '{question}'. This might mean there are no records matching your criteria, or the data might be stored differently than expected."
        else:
            return f"I found {len(results)} records related to your question: '{question}'. The data includes various financial metrics, but I wasn't able to generate a detailed explanation at this time."


class CustomSQLHandler:
    def __init__(self, openai_model: str, db_path: str):
        self.llm = ChatOpenAI(model=openai_model, temperature=0)

        db_uri = f"duckdb:///{db_path}"
        print("⚙️  Raw DB URI being loaded:", db_uri)

        try:
            # TEMPORARILY REMOVE include_tables TO DEBUG TABLE VISIBILITY
            self.db = SQLDatabase.from_uri(db_uri, sample_rows_in_table_info=0)

            # Try listing tables
            try:
                all_tables = self.db.get_usable_table_names()
                print("✅ Tables seen by LangChain:", all_tables)
            except Exception as e:
                print("❌ Could not list usable tables:", str(e))

            # Get schema info
            self.table_info = self.db.get_table_info()
        except Exception as e:
            print(f"⚠️ Could not get table info from DuckDB: {e}")
            self.db = None
            self.table_info = """
Table: fact_gl
Columns: txn_date, account_name, account_id, parent_account, sub_account, account_type, detail_type, memo_description, entity_name, amount

Table: dim_account
Columns: account_id, account, parent_account, sub_account, type, detail_type, balance
"""

        self.sql_prompt = PromptTemplate(
            input_variables=["question", "table_info"],
            template="""You are an expert financial analyst writing SQL queries for a DuckDB database.

Given the following table information:
{table_info}

IMPORTANT RULES:
- Only use these tables: fact_gl, dim_account
- Do NOT invent new tables like qbo_pl or any other tables
- Write syntactically correct DuckDB SQL
- Return ONLY the SQL query, no explanations

IMPORTANT DATA FACTS:
- The fact_gl table is the primary transaction table with normalized sign: Income and Revenue amounts are positive, Expenses and Cost of Goods Sold amounts are negative.
- fact_gl includes: txn_date, account_name, account_type, detail_type, entity_name, memo_description, amount
- dim_account holds the account hierarchy and metadata (e.g., parent, sub_account, balance)
- You can join on account_name = dim_account.account
- For any question about expenses, ensure that you filter by dim_account.type = 'Expenses'
- If the user mentions "marketing", filter:
    - dim_account.detail_type LIKE '%Marketing%'
    - OR dim_account.detail_type LIKE '%Advertising%'
    - OR dim_account.account LIKE '%Marketing%'
- When answering, keep in mind it is the year 2025 and the current date is July 14th
- YOU ONLY HAVE ACCESS TO DATA FOR THE YEAR 2025 and 2024

IMPORTANT QUERY CONSTRAINTS:
- For any question about expenses, ensure that you filter by dim_account.type = 'Expenses'
- For any question about Cost of Goods Sold, filter by dim_account.type = 'Cost of Goods Sold'
- Do NOT include other account types like 'Assets', 'Liabilities', 'Equity' when calculating income, expenses, or COGS.
- If the user asks about revenue, filter by dim_account.type = 'Income'
- For net profit, use this formula:
    Net Profit = SUM(Income amounts) + SUM(Expenses amounts) + SUM(COGS amounts)
    DO NOT negate or subtract expenses or COGS again because they are already negative.


Question: {question}

SQL Query:""",
        )

    def generate_sql(self, question: str) -> str:
        try:
            formatted_prompt = self.sql_prompt.format(question=question, table_info=self.table_info)
            response = self.llm.invoke(formatted_prompt)
            sql_query = response.content.strip()
            sql_query = self.clean_sql(sql_query)
            return sql_query
        except Exception as e:
            raise Exception(f"Failed to generate SQL: {str(e)}")

    def clean_sql(self, sql: str) -> str:
        sql = re.sub(r"```sql\n?", "", sql)
        sql = re.sub(r"```\n?", "", sql)
        sql = sql.strip()
        if not sql.endswith(";"):
            sql += ";"
        return sql

    def execute_sql(self, sql: str) -> List[Dict[str, Any]]:
        if not self.db:
            raise Exception("Database not initialized correctly.")
        try:
            print(f"🔍 Executing SQL: {sql}")
            result = self.db.run(sql)
            print(f"🔍 Raw result type: {type(result)}")
            print(f"🔍 Raw result: {result}")

            if isinstance(result, str):
                if result.strip() == "":
                    return [{"message": "No data found"}]
                return [{"result": result}]
            elif hasattr(result, "fetchall"):
                rows = result.fetchall()
                if not rows:
                    return [{"message": "No rows returned"}]
                columns = [desc[0] for desc in result.description] if result.description else []
                return [dict(zip(columns, row)) for row in rows]
            elif isinstance(result, list):
                if len(result) == 0:
                    return [{"message": "No rows returned"}]
                if isinstance(result[0], tuple):
                    return [{"result": str(row)} for row in result]
                else:
                    return result
            else:
                return [{"result": str(result)}]
        except Exception as e:
            print(f"❌ SQL execution error: {str(e)}")
            raise Exception(f"Failed to execute SQL: {str(e)}")

    def query(self, question: str) -> Dict[str, Any]:
        try:
            sql_query = self.generate_sql(question)
            print(f"🔍 Generated SQL: {sql_query}")
            results = self.execute_sql(sql_query)
            print(f"✅ Query results: {results}")
            explanation = explain_sql_results(question, sql_query, results)
            print(f"📝 Natural language explanation: {explanation}")
            return {
                "question": question,
                "generated_sql": sql_query,
                "raw_result": results,
                "explanation": explanation,
                "success": True,
            }
        except Exception as e:
            print(f"❌ Query failed: {str(e)}")
            return {
                "question": question,
                "generated_sql": "Failed to generate SQL",
                "raw_result": [],
                "explanation": f"I encountered an error while processing your question: '{question}'. {str(e)}",
                "success": False,
                "error": str(e),
            }


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sql_handler = CustomSQLHandler(openai_model=openai_model, db_path="duckdb_finance.duckdb")


@app.get("/query")
async def query_endpoint(request: Request, query: str = None):
    if query is None:
        return {"error": "Missing required query parameter: query"}

    try:
        print(f"\n📥 Received query: {query}")
        import asyncio

        def run_query():
            return sql_handler.query(query)

        response = await asyncio.wait_for(asyncio.to_thread(run_query), timeout=45)

        if response["success"]:
            return {
                "query": query,
                "generated_sql": response["generated_sql"],
                "explanation": response["explanation"],
                "raw_result": response["raw_result"],
            }
        else:
            return {"error": response["error"], "explanation": response["explanation"]}

    except asyncio.TimeoutError:
        return {"error": "Query timed out. Please try a simpler question."}
    except Exception as e:
        print("❌ Exception in query_endpoint:", str(e))
        import traceback

        traceback.print_exc()
        return {"error": str(e)}


class SQLQueryRequest(BaseModel):
    sql: str


@app.post("/query_sql")
async def run_raw_sql(payload: SQLQueryRequest):
    sql = payload.sql
    if not sql.strip().lower().startswith("select"):
        return {"error": "Only SELECT queries are allowed."}
    try:
        results = sql_handler.execute_sql(sql)
        explanation = explain_sql_results("Custom SQL query", sql, results)

        return {"results": results, "explanation": explanation, "success": True}
    except Exception as e:
        return {"error": f"SQL execution failed: {str(e)}"}


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
