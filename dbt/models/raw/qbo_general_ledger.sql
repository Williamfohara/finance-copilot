{{ config(materialized='table') }}

select
    account,
    parent_account,
    date,
    transaction_type,
    num,
    name,
    memo_description,
    split,
    amount,
    balance
from read_csv_auto('clean_data/qbo_general_ledger.csv', header = true)
