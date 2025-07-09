**Table-by-Table Breakdown**

`fact_gl` (General Ledger Facts)

Source: `general_ledger.csv`
1 row = 1 journal line

- Captures all financial activity used in downstream analysis.

| Column          | Description                              |
| --------------- | ---------------------------------------- |
| `date_id`       | Foreign key to `dim_date`                |
| `account_id`    | Foreign key to `dim_account`             |
| `amount`        | Debit or credit amount                   |
| `txn_type`      | Transaction type (Invoice, Bill, etc.)   |
| `memo`          | Line-level description                   |
| `txn_id`        | Transaction identifier                   |
| `entity_id`     | (Optional) Link to `dim_entity`          |
| `vendor_id`     | (Optional) Link to `dim_vendor`          |
| --------------- | ---------------------------------------- |

---

`dim_account` (Chart of Accounts)

- **Source**: `account_list.csv`
- Represents the structure of accounts in the sandbox ledger.

| Column       | Description                                   |
| ------------ | --------------------------------------------- |
| `account_id` | Unique name or path (e.g., "Automobile:Fuel") |
| `type`       | Top-level type (Asset, Expense, Income)       |
| `subtype`    | Detail type from QuickBooks                   |
| `is_active`  | Boolean flag for filtering inactive accounts  |
| ------------ | --------------------------------------------- |

---

`dim_date` (Calendar Dimension)

- **Generated programmatically** (not in CSVs)
- Used for time-based rollups, filtering, and variance calculations.

| Column           | Description                          |
| ---------------- | ------------------------------------ |
| `date_id`        | Primary key in `YYYY-MM-DD` format   |
| `month`          | Integer (1–12)                       |
| `quarter`        | Integer (1–4)                        |
| `year`           | Fiscal year                          |
| `is_month_end`   | Boolean flag for variance use cases  |
| ---------------- | ------------------------------------ |

---

`dim_entity` (Optional: Customers, Classes, Departments)

- **Not populated in current sandbox data**
- Reserved for future enrichment (e.g. class/location/customer in GL lines)

| Column         | Description                           |
| -------------- | ------------------------------------- |
| `entity_id`    | Composite key or hashed identifier    |
| `entity_type`  | Class, Customer, Location, etc.       |
| `name`         | Human-readable label                  |
| `region`       | Optional geographic group             |
| -------------- | ------------------------------------- |

📌 _Currently stubbed as an empty table._

---

`dim_vendor` (Optional)

- **Not present in current exports**
- Useful for vendor-level cost or AP queries.

| Column                                               | Description                       |
| ---------------------------------------------------- | --------------------------------- |
| `vendor_id`                                          | Unique ID or vendor name          |
| `category`                                           | External/Internal, supplier type  |
| `active`                                             | Boolean flag                      |
| ---------------------------------------------------- | --------------------------------- |

📌 _Currently stubbed as an empty table._

---

🧩 File Mapping

| File Name                      | Used For                |
| ------------------------------ | ----------------------- |
| `general_ledger.csv`           | `fact_gl`               |
| `account_list.csv`             | `dim_account`           |
| `balance_sheet.csv`            | Cross-check balances    |
| `pl.csv`                       | Validating P&L values   |
| _(none yet)_                   | `dim_vendor`            |
| _(none yet)_                   | `dim_entity`            |
| _(generated)_                  | `dim_date`              |
| ------------------------------ | ----------------------- |
