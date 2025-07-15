import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import subprocess

from scripts import (
    ingest_qbo,
    reshape_account_list,
    reshape_balance_sheet,
    reshape_general_ledger,
    reshape_pl,
)


def main():
    print("=== Step 1: Reshaping Data ===")
    reshape_account_list.main()
    reshape_balance_sheet.main()
    reshape_general_ledger.main()
    reshape_pl.main()

    print("=== Step 2: Loading Clean Data into DuckDB ===")
    ingest_qbo.main()

    print("=== Step 3: Building dbt Models ===")
    result = subprocess.run(["poetry", "run", "dbt", "build"], check=True)
    if result.returncode == 0:
        print("✅ dbt models built successfully")

    print("🚀 ETL + dbt pipeline complete. Data is ready for querying!")


if __name__ == "__main__":
    main()
