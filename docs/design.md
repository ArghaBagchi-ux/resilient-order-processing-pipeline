# Design Notes

## Requirements mapped to implementation

| Requirement | Implementation |
|---|---|
| Strong Python | Modular Python package, Pydantic validation, CLI, concurrency, logging |
| Linux | Makefile, shell commands, env vars, Docker workflow |
| SQL | PostgreSQL DDL, constraints, indexes, upsert, analytics |
| Fault tolerance | Retries, idempotency, dead-letter handling, audit trail |
| Data intensive | Chunked ingestion and configurable process workers |
| Attention to detail | Validation rules, metrics, tests, CI, explicit failure paths |

## Recovery model

A pipeline run can fail after some chunks have already loaded. When the same source file is rerun, `order_id` prevents duplicate rows and the upsert updates existing records. This gives the load step practical retry safety.

## Why not silently skip bad data?

Invalid records are business data that may need correction. The dead-letter table preserves the original payload and validation reason so an engineer can inspect and reprocess them later.

## Scaling path

The project is intentionally runnable on a laptop. For larger workloads, the architecture can evolve to:

```text
Applications / APIs / Kafka
          |
          v
     Object Storage
          |
        Airflow
          |
       PySpark
          |
   Lakehouse / Warehouse
          |
        BI / SQL
```

The current project is therefore a practical local implementation of patterns used in larger data platforms, not a claim of multi-machine distributed execution.
