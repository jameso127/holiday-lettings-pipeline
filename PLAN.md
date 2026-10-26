# Plan: Holiday Lettings Booking Pipeline

Timebox: 90 minutes. Stack: dbt-core + dbt-duckdb, local DuckDB file, outputs to Parquet.

## Goal

1. Ingest the raw booking CSV.
2. Clean and standardise it: missing values, types, formats.
3. Produce a summary per property: total revenue, average length of stay (days), count of cancelled vs completed bookings.
4. Write the clean dataset and the summary table to local files.

## Data profile (raw file, 200 rows, 8 columns)

| Column | Observed issues |
|---|---|
| `booking_id` | Clean, unique (`ID-1000`..`ID-1199`) |
| `property_name` | Clean, 5 distinct values |
| `guest_name` | Leading/trailing whitespace |
| `status` | Mixed case: `cancelled`, `Cancelled`, `Completed`, `COMPLETED`, `Pending` |
| `check_in_date` | 67 blank; mixed ISO `yyyy-mm-dd` and `dd/mm/yyyy` |
| `check_out_date` | Never blank; mixed ISO and `dd/mm/yyyy` |
| `daily_rate_usd` | 34 blank |
| `total_booking_value` | 23 blank; `$` prefixes, `.00` suffixes, padding spaces |

Key findings:
- **Slash dates are dd/mm**: 42 rows have first part > 12, none have second part > 12.
- **`total = rate × nights` holds for every row with both values** (143/143 give whole nights). This is the basis for imputation.
- 19 rows have a missing check-in *and* a missing rate or total. Their nights cannot be derived.

## Ingestion

- Copy the raw file to `data/raw/holiday_lettings.csv`. Never reference the Downloads path.
- Declare it as a dbt **source**, not a seed, through dbt-duckdb `external_location`:
  `read_csv('data/raw/holiday_lettings.csv', all_varchar=true, header=true)`.
- Load everything as varchar. All casting happens in staging, so nothing is lost to type inference.

## Models

```
models/
  staging/stg_bookings.sql     -- trim guest name, lowercase status, parse dates, strip currency, cast
  marts/bookings_clean.sql     -- impute check_in / rate / total, nights, flags (external: parquet)
  marts/property_summary.sql   -- summary table (external: parquet)
  schema.yml                   -- docs, tests
```
No intermediate layer: with a single source it would only be a pass-through.

### stg_bookings
- Only the cleaning the data needs: `TRIM(guest_name)` (the only padded text column), `LOWER(status)`.
- Dates: `STRPTIME(x, ['%d/%m/%Y', '%Y-%m-%d'])` tries each format, then cast to DATE.
- Money: `REPLACE(x, '$', '')` then `CAST(... AS DECIMAL(10, 2))` (the cast tolerates padding).
- Casts are **strict** (not `TRY_`): an unseen format fails the build loudly rather than silently becoming NULL.
- No `NULLIF`: DuckDB already reads empty CSV fields as NULL.

### bookings_clean
Apply in this order, and record each derivation in a flag column:
1. `check_in_date` missing and rate and total present: `check_out - (total / rate)` days.
2. `nights = check_out - check_in`.
3. `daily_rate_usd` missing: `total / nights`.
4. `total_booking_value` missing: `rate × nights`.
5. Flags: `is_check_in_imputed`, `is_rate_imputed`, `is_total_imputed`. Unknown stay is just `nights IS NULL`.

### property_summary (one row per property)
- `total_revenue_usd`: sum of `total_booking_value` where status = completed.
- `avg_length_of_stay_days`: avg(nights) across all statuses (booked length), NULLs excluded.
- `completed_bookings`, `cancelled_bookings`, `pending_bookings`, `total_bookings`.

## Assumptions (to be repeated in README)

1. Revenue counts **completed** bookings only (realised revenue). Cancelled bookings are assumed not charged; pending ones are not yet earned.
2. **Pending** is kept as its own status and reported separately, not merged or dropped. All bookings are from 2023, so every pending stay is in the past: most likely a status never updated in the legacy system. Flagged as a data-quality issue rather than guessed.
3. Slash dates are dd/mm/yyyy, based on the evidence above.
4. Currency is USD throughout (`$` prefix and the column name agree).
5. Rows whose stay length cannot be derived are kept with NULL nights and flagged, and are excluded from the average. They are not dropped and not guessed.
6. Length of stay = nights = `check_out - check_in`.

## Tests (schema.yml + singular tests)

- `booking_id`: unique, not_null
- `status`: accepted_values [completed, cancelled, pending]
- `property_name`, `check_out_date`: not_null
- singular: `check_out_date > check_in_date` where both present
- singular: `total_booking_value = daily_rate_usd * nights` where all present
- singular: summary booking counts sum to the source row count (no rows lost)

## Deliverables

- [ ] `requirements.txt` (`dbt-duckdb`), `profiles.yml` in repo, `dbt_project.yml`
- [ ] Models + tests passing with `dbt build`
- [ ] `output/bookings_clean.parquet`, `output/property_summary.parquet`
- [ ] README: how to run, assumptions, AI usage and how outputs were verified
- [ ] Spot-check: manually verify the summary for one property against the raw file

## Likely live modifications (be ready)

- Revenue by month or quarter
- Include cancelled bookings in revenue, or treat pending as completed
- Add occupancy rate or average daily rate per property
- Handle a new date format or a new property name variant
