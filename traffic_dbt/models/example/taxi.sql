{{ config(materialized='view') }}

with traffic as (
    SELECT
        time,
        traveled_d,
        avg_speed, 
        lat, 
        lon,
        speed, 
        lon_acc, 
        lat_acc
        
    FROM 
        traffic

    WHERE
        type = ' Taxi'

    ORDER BY
        time
)
SELECT * FROM traffic