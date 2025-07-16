import pandas as pd

ACCOUNT_LIST_PATH = "sample_data/qbo/account_list.csv"
OUTPUT_BALANCE_SHEET_PATH = "sample_data/qbo/balance_sheet.csv"

HEADER_LINES = ['Sandbox Company_US_1,Balance Sheet,"As of July 9, 2025",,,\n', "Total ASSETS,\n"]
FOOTER_LINE = '"Wednesday, Jul 09, 2025 09:20:19 AM GMT-7 - Accrual Basis"\n'

CATEGORY_MAP = {
    "Checking": ("Current Assets", "Bank Accounts"),
    "Savings": ("Current Assets", "Bank Accounts"),
    "Accounts Receivable (A/R)": ("Current Assets", "Accounts Receivable"),
    "Inventory Asset": ("Current Assets", "Other Current Assets"),
    "Prepaid Expenses": ("Current Assets", "Other Current Assets"),
    "Uncategorized Asset": ("Current Assets", "Other Current Assets"),
    "Undeposited Funds": ("Current Assets", "Other Current Assets"),
    "Accounts Payable (A/P)": ("Liabilities", "Current Liabilities > Accounts Payable"),
    "Mastercard": ("Liabilities", "Current Liabilities > Credit Cards"),
    "Visa": ("Liabilities", "Current Liabilities > Credit Cards"),
    "Arizona Dept. of Revenue Payable": (
        "Liabilities",
        "Current Liabilities > Other Current Liabilities",
    ),
    "Board of Equalization Payable": (
        "Liabilities",
        "Current Liabilities > Other Current Liabilities",
    ),
    "Payroll Liabilities": ("Liabilities", "Current Liabilities > Other Current Liabilities"),
    "Loan Payable": ("Liabilities", "Current Liabilities > Other Current Liabilities"),
    "Notes Payable": ("Liabilities", "Long-Term Liabilities"),
    "Opening Balance Equity": ("Equity", None),
    "Retained Earnings": ("Equity", None),
    "Owner's Equity": ("Equity", None),
}


def load_account_list(filepath):
    df = pd.read_csv(filepath, skiprows=4)
    df["Balance"] = df["Balance"].replace("[\$,]", "", regex=True).astype(float)
    df["Account"] = df["Account"].fillna("")
    return df


def generate_balance_sheet(account_df):
    lines = HEADER_LINES.copy()
    assets_total = 0
    liabilities_total = 0
    equity_total = 0

    lines.append("   Current Assets,\n")
    current_assets = account_df[
        account_df["Account"].isin(
            [
                "Checking",
                "Savings",
                "Accounts Receivable (A/R)",
                "Inventory Asset",
                "Prepaid Expenses",
                "Uncategorized Asset",
                "Undeposited Funds",
            ]
        )
    ]

    bank_accounts = current_assets[current_assets["Account"].isin(["Checking", "Savings"])]
    if not bank_accounts.empty:
        lines.append("      Bank Accounts,\n")
        bank_total = bank_accounts["Balance"].sum()
        for _, row in bank_accounts.iterrows():
            lines.append(f'         {row["Account"]},"{row["Balance"]:,.2f}"\n')
        lines.append(f'      Total Bank Accounts,"$ {bank_total:,.2f}"\n')
        assets_total += bank_total

    ar = current_assets[current_assets["Account"] == "Accounts Receivable (A/R)"]
    if not ar.empty:
        lines.append("      Accounts Receivable,\n")
        ar_total = ar.iloc[0]["Balance"]
        lines.append(f'         Accounts Receivable (A/R),"{ar_total:,.2f}"\n')
        lines.append(f'      Total Accounts Receivable,"$ {ar_total:,.2f}"\n')
        assets_total += ar_total

    other_assets = current_assets[
        current_assets["Account"].isin(
            ["Inventory Asset", "Prepaid Expenses", "Uncategorized Asset", "Undeposited Funds"]
        )
    ]
    if not other_assets.empty:
        lines.append("      Other Current Assets,\n")
        other_total = other_assets["Balance"].sum()
        for _, row in other_assets.iterrows():
            lines.append(f'         {row["Account"]},"{row["Balance"]:,.2f}"\n')
        lines.append(f'      Total Other Current Assets,"$ {other_total:,.2f}"\n')
        assets_total += other_total

    lines.append(f'   Total Current Assets,"$ {assets_total:,.2f}"\n')

    # Fixed Assets
    lines.append("   Fixed Assets,\n")

    # Truck net value
    truck_original = account_df[account_df["Account"] == "Truck:Original Cost"]["Balance"].sum()
    truck_depreciation = account_df[account_df["Account"] == "Truck:Depreciation"]["Balance"].sum()
    truck_net = truck_original + truck_depreciation

    lines.append("      Truck,\n")
    lines.append(f'         Truck:Original Cost,"{truck_original:,.2f}"\n')
    lines.append(f'         Truck:Depreciation,"{truck_depreciation:,.2f}"\n')
    lines.append(f'      Total Truck,"$ {truck_net:,.2f}"\n')

    # Equipment net value
    equipment_original = account_df[account_df["Account"] == "Equipment:Original Cost"][
        "Balance"
    ].sum()
    equipment_depreciation = account_df[account_df["Account"] == "Equipment:Depreciation"][
        "Balance"
    ].sum()
    equipment_net = equipment_original + equipment_depreciation

    lines.append("      Equipment,\n")
    lines.append(f'         Equipment:Original Cost,"{equipment_original:,.2f}"\n')
    lines.append(f'         Equipment:Depreciation,"{equipment_depreciation:,.2f}"\n')
    lines.append(f'      Total Equipment,"$ {equipment_net:,.2f}"\n')

    fixed_total = truck_net + equipment_net
    lines.append(f'   Total Fixed Assets,"$ {fixed_total:,.2f}"\n')
    assets_total += fixed_total

    lines.append(f'TOTAL ASSETS,"$ {assets_total:,.2f}"\n')

    # Liabilities
    lines.append("LIABILITIES AND EQUITY,\n")
    liabilities = account_df[
        account_df["Type"].str.contains(
            "Liabilities|Credit Card|Accounts payable", case=False, na=False
        )
    ]
    if not liabilities.empty:
        lines.append("   Liabilities,\n")
        liabilities_total = liabilities["Balance"].abs().sum()
        for _, row in liabilities.iterrows():
            lines.append(f'      {row["Account"]},"{abs(row["Balance"]):,.2f}"\n')
        lines.append(f'   Total Liabilities,"$ {liabilities_total:,.2f}"\n')

    # Equity
    equity = account_df[account_df["Type"] == "Equity"]
    if not equity.empty:
        lines.append("   Equity,\n")
        equity_total = equity["Balance"].sum()
        for _, row in equity.iterrows():
            lines.append(f'      {row["Account"]},"{row["Balance"]:,.2f}"\n')
        lines.append(f'   Total Equity,"$ {equity_total:,.2f}"\n')

    total_liabilities_equity = liabilities_total + equity_total
    lines.append(f'TOTAL LIABILITIES AND EQUITY,"$ {total_liabilities_equity:,.2f}"\n')

    lines.append(FOOTER_LINE)

    return lines


def save_balance_sheet(lines, output_path):
    with open(output_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    account_df = load_account_list(ACCOUNT_LIST_PATH)
    balance_sheet_lines = generate_balance_sheet(account_df)
    save_balance_sheet(balance_sheet_lines, OUTPUT_BALANCE_SHEET_PATH)
    print(f"Generated balance sheet saved to: {OUTPUT_BALANCE_SHEET_PATH}")
