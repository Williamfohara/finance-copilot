-- dbt/marts/dim_account.sql
{{ config(materialized='table') }}

with raw as (
    select *
    from read_csv_auto('clean_data/qbo_account_list.csv', header = true)
),

cleaned as (
    select
        account_id::integer as account_id,
        account,
        parent_account,
        sub_account,
        type,
        detail_type,
        balance::double as balance
    from raw
    where account is not null
)

select * from cleaned
