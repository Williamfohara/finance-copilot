import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker()

# Account-specific configurations
ACCOUNT_CONFIG = {
    "Checking": {
        "txn_types": ["Deposit", "Check", "Payment", "Expense"],
        "split_weights": {
            "Utilities:Gas and Electric": 0.3,
            "Marketing Expense": 0.3,
            "Automobile:Fuel": 0.4,
        },
        "amount_range": (-1000, 5000),
    },
    "Savings": {
        "txn_types": ["Deposit", "Interest"],
        "split_weights": {"Interest Income": 1.0},
        "amount_range": (50, 500),
    },
    "Accounts Receivable (A/R)": {
        "txn_types": ["Invoice", "Payment"],
        "split_weights": {"Landscaping Services": 1.0},
        "amount_range": (1000, 5000),
    },
    "Inventory Asset": {
        "txn_types": ["Invoice", "Payment", "Bill"],
        "split_weights": {"Cost of Goods Sold": 1.0},
        "amount_range": (-1500, 3000),
    },
    "Prepaid Expenses": {
        "txn_types": ["Bill", "Expense"],
        "split_weights": {"Insurance": 1.0},
        "amount_range": (-400, 1200),
    },
    "Uncategorized Asset": {
        "txn_types": ["Adjustment"],
        "split_weights": {"Other Current Assets": 1.0},
        "amount_range": (-100, 100),
    },
    "Undeposited Funds": {
        "txn_types": ["Sales Receipt"],
        "split_weights": {"Sales of Product Income": 1.0},
        "amount_range": (100, 1000),
    },
    "Truck": {
        "txn_types": ["Journal Entry"],
        "split_weights": {"Depreciation": 1.0},
        "amount_range": (-300, -100),
    },
    "Equipment": {
        "txn_types": ["Journal Entry"],
        "split_weights": {"Depreciation": 1.0},
        "amount_range": (-300, -100),
    },
    "Accounts Payable (A/P)": {
        "txn_types": ["Bill", "Bill Payment"],
        "split_weights": {"Utilities:Gas and Electric": 0.5, "Insurance": 0.5},
        "amount_range": (-500, 1500),
    },
}

VENDOR_CACHE = {}
MEMO_TEMPLATES = {
    "Depreciation": "Monthly Depreciation",
    "Insurance": "Insurance Premium",
    "Utilities:Gas and Electric": "Utility Expense",
    "Marketing Expense": "Marketing Spend",
    "Automobile:Fuel": "Fuel Expense for Truck",
    "Cost of Goods Sold": "Inventory Purchase",
    "Sales of Product Income": "Product Sale Receipt",
    "Other Current Assets": "Adjustment Entry",
    "Landscaping Services": "Landscaping Service",
}

PAYMENT_OUT_ACCOUNTS = {
    "Checking",
    "Accounts Payable (A/P)",
    "Inventory Asset",
    "Prepaid Expenses",
    "Uncategorized Asset",
    "Truck",
    "Equipment",
}


def weighted_choice(split_weights):
    splits = list(split_weights.keys())
    weights = list(split_weights.values())
    return random.choices(splits, weights=weights, k=1)[0]


def get_vendor_for_split(split):
    if split not in VENDOR_CACHE:
        VENDOR_CACHE[split] = fake.company()
    return VENDOR_CACHE[split]


def generate_budget_entries(account, start_date, year=2025):
    budget_rows = []
    quarterly_splits = ACCOUNT_CONFIG[account]["split_weights"].keys()
    current_balance = 0  # Budget entries don't affect balance tracking

    for q, month in enumerate([1, 4, 7, 10], start=1):
        for split in quarterly_splits:
            amount = round(random.uniform(1000, 5000), 2)
            budget_date = datetime(year, month, 1)

            num = f"BUD-{q:02d}-{fake.random_number(digits=3)}"
            vendor = "Internal Planning"
            memo = f"Budget for Q{q} - {split}"

            budget_rows.append(
                [
                    "",
                    budget_date.strftime("%m/%d/%Y"),
                    "Budget",
                    num,
                    vendor,
                    memo,
                    split,
                    amount,
                    current_balance,
                ]
            )

    return budget_rows


def generate_gl_with_logic(num_records_per_account=20, start_balance=20000):
    data_rows = []
    header_rows = [
        ["Sandbox Company_US_1"] + [""] * 7,
        ["General Ledger"] + [""] * 7,
        ["Jan 1, 2024 - July 9, 2025"] + [""] * 7,
        [""] * 8,
        [
            "",
            "Date",
            "Transaction Type",
            "Num",
            "Name",
            "Memo/Description",
            "Split",
            "Amount",
            "Balance",
        ],
    ]

    start_date = datetime(2024, 1, 1)

    for account, config in ACCOUNT_CONFIG.items():
        data_rows.append([account] + [""] * 7)
        current_balance = start_balance
        current_date = start_date
        ar_invoices = []

        for _ in range(num_records_per_account):
            txn_type = random.choice(config["txn_types"])
            split = weighted_choice(config["split_weights"])
            amount = round(random.uniform(*config["amount_range"]), 2)

            interval = (
                30
                if split == "Depreciation"
                else 90 if split == "Insurance" else random.randint(15, 45)
            )
            noise = random.randint(-3, 3)
            current_date += timedelta(days=interval + noise)

            vendor = get_vendor_for_split(split)
            memo = MEMO_TEMPLATES.get(split, f"{split} Transaction")

            if txn_type == "Payment" and account in PAYMENT_OUT_ACCOUNTS:
                amount = -abs(amount)

            if account == "Accounts Receivable (A/R)" and txn_type == "Invoice":
                ar_invoices.append(
                    {
                        "vendor": vendor,
                        "amount": amount * 0.9,
                        "due_date": current_date + timedelta(days=random.randint(30, 60)),
                    }
                )

            num = f"{txn_type[:3].upper()}-{fake.random_number(digits=4)}"
            current_balance += amount

            data_rows.append(
                [
                    "",
                    current_date.strftime("%m/%d/%Y"),
                    txn_type,
                    num,
                    vendor,
                    memo,
                    split,
                    amount,
                    round(current_balance, 2),
                ]
            )

            if account == "Accounts Receivable (A/R)" and txn_type == "Payment" and ar_invoices:
                invoice = ar_invoices.pop(0)
                current_date = invoice["due_date"]
                payment_amount = round(invoice["amount"], 2)
                num = f"PAY-{fake.random_number(digits=4)}"

                data_rows.append(
                    [
                        "",
                        current_date.strftime("%m/%d/%Y"),
                        "Payment",
                        num,
                        invoice["vendor"],
                        "Payment for previous invoice",
                        split,
                        payment_amount,
                        round(current_balance, 2),
                    ]
                )

        # Insert budget entries for this account
        budget_entries = generate_budget_entries(account, start_date)
        data_rows.extend(budget_entries)

        total_amount = round(current_balance - start_balance, 2)
        data_rows.append(["Total for " + account] + [""] * 6 + [total_amount])

    return pd.DataFrame(header_rows + data_rows)


if __name__ == "__main__":
    df_gl = generate_gl_with_logic(num_records_per_account=20)

    output_path = Path("./sample_data/qbo")
    output_path.mkdir(parents=True, exist_ok=True)
    df_gl.to_csv(output_path / "dummy_general_ledger_realistic.csv", header=False, index=False)

    print("Generated realistic general ledger:")
    print(df_gl.head(15))
