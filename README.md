# Holiday Lettings Booking Pipeline

dbt + DuckDB pipeline that cleans legacy booking records and summarises them per property.

## Run

Requires [uv](https://docs.astral.sh/uv/).

```
uv sync                                        # create .venv from uv.lock
uv run dbt build --profiles-dir .              # build models + run tests
uv run sqlfluff lint models/ tests/            # lint SQL
uv run duckdb -cmd "ATTACH 'holiday_lettings.duckdb' AS lettings (READ_ONLY)" -ui   # browser UI; close before dbt build
```

Outputs are written to `output/`:
- `bookings_clean.parquet`: the cleaned dataset
- `property_summary.parquet`: the summary per property

## Pipeline

TODO

## Assumptions

TODO (see PLAN.md)

## Data quality checks

TODO

## AI usage

TODO
