with source as (
    select *
    from {{ source('qbo_raw', 'qbo_general_ledger') }}
),

renamed as (
    select
        date as txn_date,
        memo_description,
        name as entity_name,
        amount::double as amount,
        case
            when account = 'Checking' and split is not null then split
            else account
        end as account_name
    from source
    where account is not null and amount is not null and date is not null
)

select * from renamed
