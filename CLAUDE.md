# CLAUDE.md

Take-home for a data engineering interview: a dbt + DuckDB pipeline that cleans holiday-letting bookings and summarises them per property. The design and assumptions are in `PLAN.md`; follow it and flag deviations, rather than silently changing it.

## Commands

```
pip install -r requirements.txt
dbt build --profiles-dir .     # run models + tests
dbt test --profiles-dir .
sqlfluff lint models/          # sqlfluff fix models/ to auto-format
```

## Conventions

- dbt layering: `staging` (cast/standardise only) → `intermediate` (business logic, imputation) → `marts` (outputs).
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
