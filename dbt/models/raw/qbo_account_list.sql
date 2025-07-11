{{ config(materialized='table') }}

select
    account_id,
    account,
    parent_account,
    sub_account,
    type,
    detail_type,
    balance
from read_csv_auto('clean_data/qbo_account_list.csv', header = true)
