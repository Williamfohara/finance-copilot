# scripts/ingest_qbo.py
from pathlib import Path

import duckdb
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "clean_data"
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "duckdb_finance.duckdb"


def load_csv(name: str) -> pd.DataFrame:
    print(f"Loading {name}.csv...")
    return pd.read_csv(DATA_DIR / f"{name}.csv")


def main():
    con = duckdb.connect(DB_PATH)

    files = {
        "raw_general_ledger": "qbo_general_ledger",
        "raw_account_list": "qbo_account_list",
        "raw_pl": "qbo_pl",
        "raw_balance_sheet": "qbo_balance_sheet",
    }

    for table, fname in files.items():
        df = load_csv(fname)
        con.execute(f"DROP TABLE IF EXISTS {table}")
        con.register("df", df)
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
        print(f"✅ Loaded {table} ({len(df)} rows)")

    con.close()


if __name__ == "__main__":
    main()
