{{ config(materialized='table') }}

select
    section,
    account,
    amount
from read_csv_auto('clean_data/qbo_pl.csv', header = true)
