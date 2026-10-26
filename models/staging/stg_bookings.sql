SELECT
    booking_id,
    property_name,
    CAST(STRPTIME(check_in_date, ['%d/%m/%Y', '%Y-%m-%d']) AS DATE)  AS check_in_date,
    CAST(STRPTIME(check_out_date, ['%d/%m/%Y', '%Y-%m-%d']) AS DATE) AS check_out_date,
    CAST(daily_rate_usd AS DECIMAL(10, 2))                           AS daily_rate_usd,
    CAST(REPLACE(total_booking_value, '$', '') AS DECIMAL(10, 2))    AS total_booking_value,
    TRIM(guest_name)                                                 AS guest_name,
    LOWER(status)                                                    AS status
FROM {{ source('raw', 'holiday_lettings') }}
