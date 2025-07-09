-- dbt/models/staging/stg_account_list.sql

{{ config(materialized='view') }}

with source as (

    select *
    from {{ source('qbo_raw', 'qbo_account_list') }}

),

renamed as (

    select
        account_id,
        account,
        parent_account,
        sub_account,
        type,
        detail_type,
        try_cast(balance as double) as balance
    from source
)

select *
from renamed
