{{ config(materialized='table') }}

select
    section,
    category,
    subcategory,
    account,
    balance
from read_csv_auto('clean_data/qbo_balance_sheet.csv', header = true)
