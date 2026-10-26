-- Mart: one row per property. Revenue counts completed bookings only.
-- Average stay is across all bookings with a known length (NULL nights are ignored).

SELECT
    property_name,
    SUM(total_booking_value) FILTER (WHERE status = 'completed') AS total_revenue_usd,
    ROUND(AVG(nights), 2)                                        AS avg_length_of_stay_days,
    COUNT(*) FILTER (WHERE status = 'completed')                 AS completed_bookings,
    COUNT(*) FILTER (WHERE status = 'cancelled')                 AS cancelled_bookings,
    COUNT(*) FILTER (WHERE status = 'pending')                   AS pending_bookings,
    COUNT(*)                                                     AS total_bookings
FROM {{ ref('bookings_clean') }}
GROUP BY property_name
ORDER BY property_name
