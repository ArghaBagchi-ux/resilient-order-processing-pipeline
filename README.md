# Resilient Order Processing Pipeline

A production-style Python + PostgreSQL data engineering project built around the requirements of a junior/entry-level Data Engineer / Python Data Engineer role.

## What this project demonstrates

- **Python:** modular ETL, validation, concurrency, CLI, logging, error handling
- **Linux:** shell commands, Makefile, environment variables, Docker workflow
- **SQL/PostgreSQL:** schema design, constraints, indexes, upserts, analytics queries
- **Fault tolerance:** retries with exponential backoff, idempotent writes, dead-letter records, run auditing
- **Data-intensive processing:** chunked CSV ingestion and process-based parallel validation
- **Engineering discipline:** type hints, tests, linting, deterministic synthetic data, CI

> Note: the local implementation uses process-based parallelism on one machine. It is intentionally designed as a foundation that can later be moved to Spark/Kafka/Airflow for true distributed execution.

## Architecture

```text
                 +------------------+
                 | orders.csv       |
                 +--------+---------+
                          |
                    Read in chunks
                          |
                          v
                 +------------------+
                 | Python Pipeline   |
                 |                  |
                 | validate/clean   |
                 | parallel workers |
                 +----+--------+----+
                      |        |
                 valid rows   bad rows
                      |        |
                      v        v
               +-----------+  +----------------+
               | PostgreSQL|  | Dead Letter     |
               | orders    |  | invalid records |
               +-----+-----+  +----------------+
                     |
                     v
               +-------------+
               | SQL Analytics|
               +-------------+

                 pipeline_runs
                 tracks every run
```

## Project structure

```text
resilient_order_pipeline/
├── .github/workflows/ci.yml
├── data/.gitkeep
├── docs/design.md
├── sql/schema.sql
├── sql/analytics.sql
├── src/
│   ├── db/connection.py
│   ├── db/init_db.py
│   ├── generate_data.py
│   ├── load.py
│   ├── models.py
│   ├── pipeline.py
│   └── transform.py
├── tests/
│   ├── test_generate_data.py
│   └── test_transform.py
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick start

### 1. Start PostgreSQL

```bash
docker compose up -d postgres
```

### 2. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the database

```bash
export DATABASE_URL="postgresql://pipeline:pipeline@localhost:5432/pipeline_db"
```

### 4. Create tables and indexes

```bash
python -m src.db.init_db
```

### 5. Generate sample data

```bash
python -m src.generate_data --rows 100000 --output data/orders.csv --seed 42
```

The generator intentionally inserts a small number of invalid records so the dead-letter path can be demonstrated.

### 6. Run the pipeline

```bash
python -m src.pipeline --input data/orders.csv --workers 4 --chunk-size 5000
```

### 7. Run tests and lint

```bash
pytest -q
ruff check src tests
```

## Useful SQL

```bash
psql "$DATABASE_URL"
```

Then:

```sql
SELECT * FROM pipeline_runs ORDER BY started_at DESC;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM dead_letter_orders;
```

Analytics queries are in `sql/analytics.sql`.

## Fault-tolerance design

### 1. Retry with exponential backoff

Transient PostgreSQL failures are retried automatically. The retry policy uses exponential backoff so the application does not immediately hammer an unavailable database.

### 2. Idempotent loading

`order_id` is the primary key. The loader uses PostgreSQL `ON CONFLICT ... DO UPDATE`, so rerunning the same input does not create duplicate orders.

### 3. Dead-letter handling

Invalid rows are not silently discarded. The original payload, source line and validation error are stored in `dead_letter_orders` for investigation and reprocessing.

### 4. Run auditing

Every pipeline execution gets a `run_id` and is recorded in `pipeline_runs` with counts for read, valid, loaded and rejected records.

### 5. Chunked ingestion

The CSV is processed in chunks instead of loading the entire file into memory.

### 6. Controlled concurrency

Validation is CPU-parallelized with `ProcessPoolExecutor`. Worker count is configurable from the command line.

## Failure scenarios handled

| Failure | Behavior |
|---|---|
| Invalid input path | Pipeline fails fast with a clear error |
| Bad row | Row goes to dead-letter storage |
| Temporary DB failure | DB operation is retried with backoff |
| Duplicate order | Idempotent upsert updates existing row |
| Pipeline exception | Run is marked `FAILED` with metrics |
| Re-running same file | No duplicate primary keys |


## GitHub commands

```bash
git init
git add .
git commit -m "Build resilient order processing pipeline"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/resilient-order-processing-pipeline.git
git push -u origin main
```

Do not commit `.env`, database passwords, `.venv`, generated datasets, or other secrets.
