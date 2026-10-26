-- The summary must account for every booking: no rows dropped between raw, clean and summary.

WITH source_count AS (

    SELECT COUNT(*) AS booking_count FROM {{ source('raw', 'holiday_lettings') }}

),

clean_count AS (

    SELECT COUNT(*) AS booking_count FROM {{ ref('bookings_clean') }}

),

summary_count AS (

    SELECT SUM(total_bookings) AS booking_count FROM {{ ref('property_summary') }}

)

SELECT
    source_count.booking_count  AS source_bookings,
    clean_count.booking_count   AS clean_bookings,
    summary_count.booking_count AS summary_bookings
FROM source_count
CROSS JOIN clean_count
CROSS JOIN summary_count
WHERE
    source_count.booking_count <> clean_count.booking_count
    OR source_count.booking_count <> summary_count.booking_count
