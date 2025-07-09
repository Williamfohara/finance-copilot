-- dbt/models/staging/stg_balance_sheet.sql

{{ config(materialized='view') }}

with source as (
    select * from {{ source('qbo_raw', 'qbo_balance_sheet') }}
),

renamed as (
    select
        section,
        category,
        subcategory,
        account,
        try_cast(balance as double) as balance
    from source
    where account is not null
)

select * from renamed
