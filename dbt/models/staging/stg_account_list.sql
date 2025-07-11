-- dbt/models/staging/stg_account_list.sql
{{ config(materialized='table') }}

with source as (
    select * from {{ source('qbo_raw', 'qbo_account_list') }}
),

renamed as (
    select
        account_id,
        account as account_name,
        parent_account,
        sub_account,
        type as account_type,
        detail_type,
        try_cast(balance as double) as balance
    from source
    where account is not null
)

select * from renamed
