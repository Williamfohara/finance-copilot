{{ config(materialized='table') }}

select
    date,
    transaction_type,
    memo,
    name,
    account,
    debit,
    credit
from read_csv_auto('clean_data/qbo_general_ledger.csv', header = true)
