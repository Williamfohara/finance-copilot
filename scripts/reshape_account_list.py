import pandas as pd


def main():
    # --- Step 0: Load raw CSV ---
    raw_path = "sample_data/qbo/account_list.csv"
    df_raw = pd.read_csv(raw_path, header=None, skip_blank_lines=False)

    # --- Step 1: Detect real header row ---
    header_idx = df_raw[df_raw.iloc[:, 1] == "Account"].index[0]
    df = pd.read_csv(raw_path, skiprows=header_idx + 1)

    # --- Step 2: Rename columns ---
    df.columns = ["unused", "account", "type", "detail_type", "description", "balance"]
    df = df.dropna(subset=["account", "type"])

    # --- Step 3: Clean balance column ---
    df["balance"] = (
        df["balance"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
        .replace("", "0")
        .astype(float)
    )

    # --- Step 4: Normalize account types (remove QuickBooks-style tags like "(A/R)") ---
    df["type"] = df["type"].str.replace(r"\s*\(.*\)", "", regex=True).str.strip()

    # --- Step 5: Parse account hierarchy (Truck:Depreciation → parent + sub) ---
    df[["parent_account", "sub_account"]] = df["account"].str.split(":", n=1, expand=True)

    df["sub_account"] = df["sub_account"].fillna(df["account"])
    df["parent_account"] = df["parent_account"].where(df["account"].str.contains(":"), None)

    # --- Step 6: Create stable account ID for joins ---
    df["account_id"] = df["account"].astype("category").cat.codes

    # --- Step 7: Final column selection ---
    df_cleaned = df[
        [
            "account_id",
            "account",
            "parent_account",
            "sub_account",
            "type",
            "detail_type",
            "balance",
        ]
    ]

    # ✅ Preview result
    print(df_cleaned.head())

    # --- Save to cleaned CSV ---
    df_cleaned.to_csv("clean_data/qbo_account_list.csv", index=False)
    print("✅ Saved cleaned account list to clean_data/qbo_account_list.csv")


if __name__ == "__main__":
    main()
