{{ config(materialized='table') }}

select *
from read_csv_auto('clean_data/qbo_pl.csv')