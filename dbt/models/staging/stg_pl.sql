-- dbt/models/staging/stg_pl.sql

{{ config(materialized='view') }}

with source as (
    select * from {{ source('qbo_raw', 'qbo_pl') }}
),

cleaned as (
    select
        section,
        account,
        try_cast(amount as double) as amount
    from source
    where account is not null
)

select * from cleaned
