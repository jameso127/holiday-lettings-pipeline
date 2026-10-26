# CLAUDE.md

Take-home for a data engineering interview: a dbt + DuckDB pipeline that cleans holiday-letting bookings and summarises them per property. The design and assumptions are in `PLAN.md`; follow it and flag deviations, rather than silently changing it.

## Commands

```
uv sync                                    # dependencies in pyproject.toml / uv.lock
uv run dbt build --profiles-dir .          # run models + tests
uv run sqlfluff lint models/ tests/        # sqlfluff fix to auto-format
uv run duckdb -cmd "ATTACH 'holiday_lettings.duckdb' AS lettings (READ_ONLY)" -ui   # browser UI; never use -readonly with -ui
```
On Windows any open connection to `holiday_lettings.duckdb` (even read-only) locks it and makes `dbt build` fail. Query `output/*.parquet` instead, or close the connection before building.
On Windows, set `PYTHONIOENCODING=utf-8` when piping sqlfluff output, or it crashes printing an emoji and exits 1.

## Conventions

- dbt layering: `staging` (cast/standardise only) → `marts` (imputation, aggregation, outputs). No intermediate layer: with one source it would be a pass-through.
- Keep SQL minimal: only clean what the data actually needs, and let tests catch new problems.
- DuckDB SQL dialect. CTEs over subqueries, one model per file, `snake_case` identifiers.
- Style is enforced by sqlfluff (`.sqlfluff`): UPPERCASE keywords/functions/types, aligned `AS` aliases, explicit table aliases of 3+ characters. Run `sqlfluff lint models/` before finishing; `sqlfluff fix` for layout.
- Raw data is read only from `data/raw/holiday_lettings.csv` via the dbt source. Never hardcode absolute paths, and never use a seed for the raw file.
- Source columns are loaded as varchar. Do all casting in `stg_bookings`, with strict casts so unexpected formats fail loudly.
- Every new model column with a non-obvious rule gets a description in `schema.yml`. Every cleaning rule should have a test that proves it.

## Rules

- Never fabricate data. If a value can't be derived from the row, leave it NULL and set a flag column.
- Don't change assumptions (revenue definition, status handling, date format) without asking. They are deliberate and get discussed in the interview.
- Never modify `data/raw/`.
- Keep it small: this is a 90-minute task. No macros, packages, or abstractions unless they remove real duplication.
- After changes, run `dbt build` and report the actual test results.
