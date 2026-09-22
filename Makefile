.PHONY: install db-up db-down db-init generate run test lint clean

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-init:
	python -m src.db.init_db

generate:
	python -m src.generate_data --rows 100000 --output data/orders.csv --seed 42

run:
	python -m src.pipeline --input data/orders.csv --workers 4 --chunk-size 5000

test:
	pytest -q

lint:
	ruff check src tests

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__ src/__pycache__ tests/__pycache__ data/*.csv
