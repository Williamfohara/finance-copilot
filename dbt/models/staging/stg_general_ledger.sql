-- dbt/models/staging/stg_general_ledger.sql

{{ config(materialized='view') }}

with source as (
    select * from {{ source('qbo_raw', 'qbo_general_ledger') }}
),

renamed as (
    select
        account,
        parent_account,
        try_cast(date as date) as txn_date,
        transaction_type,
        num,
        name,
        memo_description,
        split,
        try_cast(amount as double) as amount,
        try_cast(balance as double) as balance
    from source
)

select * from renamed
