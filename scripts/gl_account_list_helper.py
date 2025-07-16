from datetime import datetime

import pandas as pd

ACCOUNT_LIST_PATH = "sample_data/qbo/account_list.csv"
GENERAL_LEDGER_PATH = "sample_data/qbo/dummy_general_ledger.csv"
OUTPUT_ACCOUNT_LIST_PATH = "sample_data/qbo/updated_account_list.csv"

HEADER_LINES = ["Sandbox Company_US_1,,,,,\n", "Account List,,,,,\n", ",,,,,\n", ",,,,,\n"]

FOOTER_LINE = f'"{datetime.now().strftime("%A, %b %d, %Y %I:%M:%S %p GMT-7")}",,,,,\n'


def load_account_list(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, skiprows=4)
    df["Balance"] = df["Balance"].replace("[\$,]", "", regex=True).astype(float)
    return df


def load_general_ledger(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, skiprows=4)
    df["Amount"] = df["Amount"].replace("[\$,]", "", regex=True).astype(float)
    return df


def update_account_balances(account_df: pd.DataFrame, gl_df: pd.DataFrame) -> pd.DataFrame:
    gl_summary = (
        gl_df.groupby("Split", as_index=False)["Amount"]
        .sum()
        .rename(columns={"Amount": "GL_Balance"})
    )
    updated_accounts = pd.merge(
        account_df, gl_summary, left_on="Account", right_on="Split", how="left"
    )
    updated_accounts["Balance"] = updated_accounts["GL_Balance"].fillna(updated_accounts["Balance"])
    updated_accounts = updated_accounts.drop(columns=["Split", "GL_Balance"])
    return updated_accounts


def save_account_list_with_formatting(df: pd.DataFrame, output_path: str):
    with open(output_path, "w") as f:
        for line in HEADER_LINES:
            f.write(line)

        df_to_save = df.copy()
        df_to_save["Balance"] = df_to_save["Balance"].map(lambda x: f"{x:,.2f}")
        df_to_save.to_csv(f, index=False, header=True, lineterminator="\n")

        f.write(",,,,,\n")
        f.write(",,,,,\n")
        f.write(FOOTER_LINE)


if __name__ == "__main__":
    account_df = load_account_list(ACCOUNT_LIST_PATH)
    gl_df = load_general_ledger(GENERAL_LEDGER_PATH)
    updated_accounts = update_account_balances(account_df, gl_df)
    save_account_list_with_formatting(updated_accounts, OUTPUT_ACCOUNT_LIST_PATH)
    print(f"Updated account list with GL balances saved to: {OUTPUT_ACCOUNT_LIST_PATH}")
