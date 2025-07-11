-- dbt/models/staging/stg_general_ledger.sql
{{ config(materialized='table') }}

with source as (
    select *
    from {{ source('qbo_raw', 'qbo_general_ledger') }}
),

renamed as (
    select
        date as txn_date,
        account as account_name,
        memo_description,
        name as entity_name,
        amount::double as amount  -- or try_cast(amount as double)
    from source
    where account is not null and amount is not null and date is not null
)

select * from renamed
