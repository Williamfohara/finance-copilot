{{ config(materialized='table') }}

with source as (
    select *
    from {{ source('qbo_raw', 'qbo_pl') }}
),

renamed as (
    select
        section,
        account,
        try_cast(amount as double) as amount
    from source
    where account is not null
)

select * from renamed
