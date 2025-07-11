-- dbt/models/marts/fact_gl.sql
{{ config(materialized='table') }}

with gl as (
    select * from {{ ref('stg_general_ledger') }}
),

acct as (
    select * from {{ ref('dim_account') }}
),

joined as (
    select
        gl.txn_date,
        gl.account_name,
        acct.account_id,
        acct.parent_account,
        acct.sub_account,
        acct.type as account_type,
        acct.detail_type,
        gl.memo_description,
        gl.entity_name,
        case
            when acct.type = 'Expenses' then -1 * abs(gl.amount)
            when acct.type = 'Cost of Goods Sold' then -1 * abs(gl.amount)
            else gl.amount
        end as amount
    from gl
    left join acct
        on gl.account_name = acct.account
)

select * from joined
