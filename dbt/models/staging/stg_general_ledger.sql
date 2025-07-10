{{ config(materialized='view') }}

with source as (
    select *
    from {{ source('qbo_raw', 'qbo_general_ledger') }}
),

renamed as (
    select
        txn_date,
        account,
        description,
        memo,
        name,
        amount::double as amount  -- or try_cast(amount as double)
    from source
    where account is not null and is_active = true
)

select * from renamed
