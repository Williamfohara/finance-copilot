import pandas as pd

# --- Step 0: Load file ---
raw_path = "sample_data/qbo/general_ledger.csv"
df_raw = pd.read_csv(raw_path, header=None, skip_blank_lines=False)

# --- Step 1: Prepare ---
records = []
current_account = None

# --- Step 2: Iterate row by row ---
for _, row in df_raw.iterrows():
    cells = row.fillna("").astype(str).str.strip().tolist()

    # Skip header/footer rows
    if (
        "general ledger" in cells[0].lower()
        or "sandbox" in cells[0].lower()
        or "basis" in cells[0].lower()
        or "july" in cells[0].lower()
        or cells[0] == "" and all(c == "" for c in cells[1:])
    ):
        continue

    # Detect account name (only column 0 has value)
    if cells[0] and not any(cells[1:]):
        current_account = cells[0]
        continue

    # Skip totals
    if "total for" in cells[0].lower():
        continue

    # Capture rows with data (either beginning balance or real transaction)
    is_transaction = pd.to_datetime(cells[1], errors="coerce") is not pd.NaT
    is_beginning = cells[1].lower() == "beginning balance"

    if is_transaction or is_beginning:
        record = {
            "account": current_account,
            "parent_account": None,  # ✅ placeholder for future enrichment
            "date": pd.to_datetime(cells[1], errors="coerce").date() if is_transaction else None,
            "transaction_type": cells[2] if is_transaction else "Beginning Balance",
            "num": cells[3] if is_transaction else None,
            "name": cells[4] if is_transaction else None,
            "memo_description": cells[5] if is_transaction else None,
            "split": cells[6] if is_transaction else None,
            "amount": None,
            "balance": None,
        }

        # Clean amount
        amt_raw = cells[7].replace(",", "").replace("(", "-").replace(")", "").strip()
        if amt_raw:
            try:
                record["amount"] = float(amt_raw)
            except ValueError:
                pass

        # Clean balance
        if len(cells) > 8:
            bal_raw = cells[8].replace(",", "").replace("(", "-").replace(")", "").strip()
            if bal_raw:
                try:
                    record["balance"] = float(bal_raw)
                except ValueError:
                    pass

        records.append(record)

# --- Step 3: Create clean DataFrame ---
df_cleaned = pd.DataFrame(records)

# --- Step 4: Preview + save ---
print(df_cleaned.head())
df_cleaned.to_csv("clean_data/qbo_general_ledger.csv", index=False)
