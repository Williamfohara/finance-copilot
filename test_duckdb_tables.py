# test_duckdb_tables.py

import duckdb

# Path to your DuckDB database
db_path = "duckdb_finance.duckdb"

# Connect and run a query to list all tables/views in the 'main' schema
try:
    con = duckdb.connect(db_path)
    result = con.execute(
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_type, table_name
    """
    ).fetchall()

    print("✅ Tables and Views in DuckDB:")
    for row in result:
        print(f"- {row[0]} ({row[1]})")

except Exception as e:
    print(f"❌ Error accessing DuckDB: {e}")
