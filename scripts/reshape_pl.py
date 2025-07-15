import pandas as pd


def main():
    # --- Step 0: Load raw file ---
    raw_path = "sample_data/qbo/pl.csv"
    df_raw = pd.read_csv(raw_path, header=None, skip_blank_lines=False)

    # --- Step 1: Prepare ---
    records = []
    current_section = None

    # --- Step 2: Iterate through rows ---
    for _, row in df_raw.iterrows():
        label = str(row[0]).strip() if pd.notnull(row[0]) else ""
        value = str(row[1]).strip() if pd.notnull(row[1]) else ""

        # Skip metadata and footers
        if any(
            [
                "Sandbox" in label,
                "Profit and Loss" in label,
                "Accrual Basis" in label,
                label == "" and value == "",
            ]
        ):
            continue

        # Detect section headers
        if value == "" and not label.endswith(":") and label.isalpha():
            current_section = label
            continue

        # Skip subtotal/total rows
        if label.lower().startswith("total for") or label.lower().startswith("net"):
            continue

        # Attempt to parse a data row
        try:
            amount = (
                value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "").strip()
            )
            amount = float(amount)
            records.append({"section": current_section, "account": label, "amount": amount})
        except ValueError:
            continue

    # --- Step 3: To clean DataFrame ---
    df_cleaned = pd.DataFrame(records)

    # --- Step 4: Preview and save ---
    print(df_cleaned.head())
    df_cleaned.to_csv("clean_data/qbo_pl.csv", index=False)
    print("✅ Saved cleaned P&L to clean_data/qbo_pl.csv")


if __name__ == "__main__":
    main()
