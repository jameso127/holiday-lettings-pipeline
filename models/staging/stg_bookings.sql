-- Staging: trim strings, lowercase status, parse ISO + dd/mm/yyyy dates, strip '$' and cast money.
-- Source: {{ source('raw', 'holiday_lettings') }} (all varchar). No business logic here.


SELECT 
FROM {{ source('raw', 'holiday_lettings') }}