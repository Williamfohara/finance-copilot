import pandas as pd

ACCOUNT_LIST_PATH = "sample_data/qbo/account_list.csv"
GL_PATH = "sample_data/qbo/general_ledger.csv"
OUTPUT_PL_PATH = "sample_data/qbo/pl.csv"

HEADER_LINES = [
    "Profit and Loss,\n",
    "Sandbox Company_US_1,\n",
    '"January 1, 2024 – July 9, 2025",\n',
    ",\n",
    "Distribution account,Total\n",
]
FOOTER_LINE = '"Accrual Basis Wednesday, July 09, 2025 04:19 PM GMT-7",\n'

CATEGORIES = {
    "Income": [
        "Design income",
        "Discounts given",
        "Landscaping Services",
        "Pest Control Services",
        "Sales of Product Income",
        "Services",
    ],
    "Job Materials": ["Decks and Patios", "Fountains and Garden Lighting", "Plants and Soil"],
    "Labor": ["Installation", "Maintenance and Repair"],
    "Cost of Goods Sold": ["Cost of Goods Sold"],
    "Expenses": [
        "Automobile",
        "Automobile:Fuel",
        "Equipment Rental",
        "Insurance",
        "Job Expenses:Cost of Labor",
        "Job Expenses:Job Materials",
        "Stationery & Printing",
        "Taxes & Licenses",
        "Utilities:Gas and Electric",
        "Office Expenses",
    ],
    "Other Expenses": ["Depreciation", "Interest Expense"],
}


def load_general_ledger(filepath):
    df = pd.read_csv(filepath, skiprows=4)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={"Split": "Account", "Amount": "Amount", "Balance": "Balance"})
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df


def generate_pl(gl_df):
    lines = HEADER_LINES.copy()

    # Income
    lines.append("Income,\n")
    income_total = 0
    job_materials_total = 0
    labor_total = 0

    for acct in CATEGORIES["Income"]:
        amt = gl_df[gl_df["Account"] == acct]["Amount"].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        income_total += amt

    # Job Materials
    for acct in CATEGORIES["Job Materials"]:
        amt = gl_df[gl_df["Account"] == f"Landscaping Services:Job Materials:{acct}"][
            "Amount"
        ].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        job_materials_total += amt
    lines.append(f'Total for Job Materials,"$ {job_materials_total:,.2f}"\n')

    # Labor
    for acct in CATEGORIES["Labor"]:
        amt = gl_df[gl_df["Account"] == f"Landscaping Services:Labor:{acct}"]["Amount"].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        labor_total += amt
    lines.append(f'Total for Labor,"$ {labor_total:,.2f}"\n')

    landscaping_total = gl_df[gl_df["Account"] == "Landscaping Services"]["Amount"].sum()
    landscaping_total += job_materials_total + labor_total
    lines.append(f'Total for Landscaping Services,"$ {landscaping_total:,.2f}"\n')

    total_income = income_total + job_materials_total + labor_total
    lines.append(f'Total for Income,"$ {total_income:,.2f}"\n')

    # COGS
    lines.append("Cost of Goods Sold,\n")
    cogs = gl_df[gl_df["Account"] == "Cost of Goods Sold"]["Amount"].sum()
    lines.append(f'Cost of Goods Sold,"{cogs:,.2f}"\n')
    lines.append(f'Total for Cost of Goods Sold,"$ {cogs:,.2f}"\n')

    gross_profit = total_income - cogs
    lines.append(f'Gross Profit,"$ {gross_profit:,.2f}"\n')

    # Expenses
    lines.append("Expenses,\n")
    expenses_total = 0

    auto = gl_df[gl_df["Account"] == "Automobile"]["Amount"].sum()
    fuel = gl_df[gl_df["Account"] == "Automobile:Fuel"]["Amount"].sum()
    lines.append(f'Automobile,"{auto:,.2f}"\n')
    lines.append(f'Fuel,"{fuel:,.2f}"\n')
    lines.append(f'Total for Automobile,"$ {(auto + fuel):,.2f}"\n')
    expenses_total += auto + fuel

    for acct in ["Equipment Rental", "Insurance"]:
        amt = gl_df[gl_df["Account"] == acct]["Amount"].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        expenses_total += amt

    cost_of_labor = gl_df[gl_df["Account"] == "Job Expenses:Cost of Labor"]["Amount"].sum()
    job_materials = gl_df[gl_df["Account"] == "Job Expenses:Job Materials"]["Amount"].sum()
    lines.append("Job Expenses,0.00\n")
    lines.append(f'Cost of Labor,"{cost_of_labor:,.2f}"\n')
    lines.append(f'Job Materials,"{job_materials:,.2f}"\n')
    lines.append(f'Total for Job Expenses,"$ {(cost_of_labor + job_materials):,.2f}"\n')
    expenses_total += cost_of_labor + job_materials

    for acct in [
        "Stationery & Printing",
        "Taxes & Licenses",
        "Utilities:Gas and Electric",
        "Office Expenses",
    ]:
        amt = gl_df[gl_df["Account"] == acct]["Amount"].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        expenses_total += amt

    lines.append(f'Total for Expenses,"$ {expenses_total:,.2f}"\n')

    net_operating_income = gross_profit - expenses_total
    lines.append(f'Net Operating Income,"$ {net_operating_income:,.2f}"\n')

    lines.append("Other Income,0.00\n")

    lines.append("Other Expenses,\n")
    other_expenses_total = 0
    for acct in CATEGORIES["Other Expenses"]:
        amt = gl_df[gl_df["Account"] == acct]["Amount"].sum()
        lines.append(f'{acct},"{amt:,.2f}"\n')
        other_expenses_total += amt
    lines.append(f'Total for Other Expenses,"$ {other_expenses_total:,.2f}"\n')

    net_other_income = -other_expenses_total
    lines.append(f'Net Other Income,"$ {net_other_income:,.2f}"\n')

    net_income = net_operating_income + net_other_income
    lines.append(f'Net Income,"$ {net_income:,.2f}"\n')

    lines.append(",\n,\n,\n")
    lines.append(FOOTER_LINE)

    return lines


def save_pl(lines, output_path):
    with open(output_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    gl_df = load_general_ledger(GL_PATH)
    print("Columns in loaded general ledger:", gl_df.columns.tolist())  # Debug
    pl_lines = generate_pl(gl_df)
    save_pl(pl_lines, OUTPUT_PL_PATH)
    print(f"Generated P&L statement saved to: {OUTPUT_PL_PATH}")
