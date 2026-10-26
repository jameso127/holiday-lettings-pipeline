# Holiday Lettings Booking Pipeline

dbt + DuckDB pipeline that cleans legacy booking records and summarises them per property.

## Run

```
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
dbt build --profiles-dir .
sqlfluff lint models/
```

Outputs are written to `output/`:
- `bookings_clean.parquet` / `.csv`: the cleaned dataset
- `property_summary.parquet` / `.csv`: the summary per property

## Pipeline

TODO

## Assumptions

TODO (see PLAN.md)

## Data quality checks

TODO

## AI usage

TODO
