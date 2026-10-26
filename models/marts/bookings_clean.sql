-- Mart: one row per booking, with gaps filled using total = daily rate x nights (holds for every complete raw row).
-- Values that cannot be derived stay NULL. Each derived value is flagged.

WITH bookings AS (

    SELECT
        *,
        CAST(
            COALESCE(
                check_out_date - check_in_date,
                total_booking_value / daily_rate_usd
            )
            AS INTEGER
        ) AS nights
    FROM {{ ref('stg_bookings') }}

)

SELECT
    booking_id,
    property_name,
    guest_name,
    status,
    check_out_date,
    nights,
    check_out_date - nights                                                           AS check_in_date,
    COALESCE(daily_rate_usd, CAST(total_booking_value / nights AS DECIMAL(10, 2)))    AS daily_rate_usd,
    COALESCE(total_booking_value, daily_rate_usd * nights)                            AS total_booking_value,
    check_in_date IS NULL AND nights IS NOT NULL                                      AS is_check_in_imputed,
    daily_rate_usd IS NULL AND total_booking_value IS NOT NULL AND nights IS NOT NULL AS is_rate_imputed,
    total_booking_value IS NULL AND daily_rate_usd IS NOT NULL AND nights IS NOT NULL AS is_total_imputed
FROM bookings
