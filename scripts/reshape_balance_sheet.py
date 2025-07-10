import pandas as pd

# --- Step 0: Load raw data ---
raw_path = "sample_data/qbo/balance_sheet.csv"
df_raw = pd.read_csv(raw_path, header=None, skip_blank_lines=False)

# --- Step 1: Init ---
records = []
section = category = subcategory = None

# --- Step 2: Iterate ---
for _, row in df_raw.iterrows():
    label_raw = str(row[0]) if pd.notnull(row[0]) else ""
    value_raw = str(row[1]) if pd.notnull(row[1]) else ""

    # Clean and count indentation
    label = label_raw.strip()
    value = value_raw.strip().replace("$", "").replace(",", "")
    indent_level = len(label_raw) - len(label_raw.lstrip())

    # Skip header/footer
    if (
        label.startswith("Sandbox")
        or label.startswith("Balance Sheet")
        or "Basis" in label
    ):
        continue
    if label == "" and value == "":
        continue

    # Update section/category/subcategory
    if indent_level == 0 and value == "":
        section = label
        category = subcategory = None
        continue
    elif indent_level == 3 and value == "":
        category = label
        subcategory = None
        continue
    elif indent_level == 6 and value == "":
        subcategory = label
        continue
    elif indent_level >= 9 and value:
        # Actual data row
        try:
            balance = float(value)
        except ValueError:
            continue

        records.append(
            {
                "section": section,
                "category": category,
                "subcategory": subcategory,
                "account": label,
                "balance": balance,
            }
        )

# --- Step 3: DataFrame ---
df_cleaned = pd.DataFrame(records)

# --- Step 4: Output ---
print(df_cleaned.head())
df_cleaned.to_csv("clean_data/qbo_balance_sheet.csv", index=False)
