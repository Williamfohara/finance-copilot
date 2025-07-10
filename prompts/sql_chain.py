from langchain.prompts import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai import ChatOpenAI


def create_custom_sql_chain(openai_model: str, db_path: str) -> SQLDatabaseChain:
    llm = ChatOpenAI(model=openai_model, temperature=0)

    db = SQLDatabase.from_uri(
        f"duckdb:///{db_path}",
        include_tables=[
            "raw_pl",
            "raw_general_ledger",
            "raw_account_list",
            "raw_balance_sheet",
        ],
    )

    _CUSTOM_SQL_PROMPT = PromptTemplate(
        input_variables=["query"],
        template="""
You are an expert financial analyst writing SQL queries for a DuckDB database using tables like
`raw_pl`, `raw_general_ledger`, `raw_account_list`, and `raw_balance_sheet`.

ONLY use these tables. Do NOT invent new ones like `qbo_pl`.

Example:
Q: What did we spend on marketing in Q1?
SQLQuery:
SELECT account, amount
FROM raw_pl
WHERE section = 'Expense'
  AND account LIKE '%Marketing%'
  AND date BETWEEN '2023-01-01' AND '2023-03-31';

Now write a SQL query to answer this question:
Q: {query}
SQLQuery:
""",
    )

    return SQLDatabaseChain.from_llm(
        llm=llm,
        db=db,
        prompt=_CUSTOM_SQL_PROMPT,
        verbose=True,
        return_intermediate_steps=True,
        input_key="query",
    )
