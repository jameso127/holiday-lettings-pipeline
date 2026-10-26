-- Raw and imputed values must agree: total = daily rate x nights wherever all three are known.

SELECT
    booking_id,
    daily_rate_usd,
    nights,
    total_booking_value
FROM {{ ref('bookings_clean') }}
WHERE total_booking_value <> daily_rate_usd * nights
