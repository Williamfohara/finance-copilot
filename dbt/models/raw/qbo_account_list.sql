{{ config(materialized='table') }}

select
    "Account ID" as account_id,
    "Account Name" as account_name,
    "Parent Account" as parent_account,
    "Sub-Account" as sub_account,
    "Type" as acct_type,         -- ✅ changed alias to `acct_type`
    "Detail Type" as acct_detail_type,  -- ✅ changed alias to `acct_detail_type`
    balance
from read_csv_auto('clean_data/qbo_account_list.csv', header = true)
