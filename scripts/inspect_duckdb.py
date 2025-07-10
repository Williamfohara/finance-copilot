# scripts/inspect_duckdb.py
import duckdb

DB_PATH = "data/duckdb_finance.duckdb"


def main():
    con = duckdb.connect(DB_PATH)

    # List all tables
    print("\n📋 Tables in database:")
    tables = con.execute("SHOW TABLES").fetchall()
    for (table_name,) in tables:
        print(f" - {table_name}")

        # Show schema for each table
        print("   Schema:")
        schema = con.execute(f"DESCRIBE {table_name}").fetchall()
        for col in schema:
            print(f"     {col[0]} ({col[1]})")

    con.close()


if __name__ == "__main__":
    main()
