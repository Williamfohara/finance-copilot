# scripts/load_to_duckdb.py
import duckdb

con = duckdb.connect("duckdb_finance.duckdb")

tables = {
    "raw_account_list": "clean_data/qbo_account_list.csv",
    "raw_balance_sheet": "clean_data/qbo_balance_sheet.csv",
    "raw_general_ledger": "clean_data/qbo_general_ledger.csv",
    "raw_pl": "clean_data/qbo_pl.csv",
}

for table, path in tables.items():
    con.execute(
        f"""
        CREATE OR REPLACE TABLE {table} AS
        SELECT * FROM read_csv_auto('{path}', header=True)
    """
    )
    print(f"✅ Loaded {table}")

con.close()
