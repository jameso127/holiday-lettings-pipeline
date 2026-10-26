-- Every booking with both dates must end after it starts.

SELECT
    booking_id,
    check_in_date,
    check_out_date
FROM {{ ref('bookings_clean') }}
WHERE check_out_date <= check_in_date
