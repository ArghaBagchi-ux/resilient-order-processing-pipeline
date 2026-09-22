import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

STATUSES = ["completed", "pending", "cancelled"]
COUNTRIES = ["IN", "US", "GB", "DE", "SG"]


def generate(rows: int, output: str, seed: int = 42):
    random.seed(seed)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "order_id", "customer_id", "product_id", "country",
            "quantity", "unit_price", "status", "order_ts"
        ])
        for order_id in range(1, rows + 1):
            quantity = random.randint(1, 5)
            status = random.choice(STATUSES)
            if order_id % 10000 == 0:
                quantity = -1
            writer.writerow([
                order_id,
                random.randint(1000, 9999),
                random.randint(100, 999),
                random.choice(COUNTRIES),
                quantity,
                round(random.uniform(5, 500), 2),
                status,
                start + timedelta(minutes=random.randint(0, 500000)),
            ])

    print(f"Generated {rows} rows at {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--output", default="data/orders.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.rows < 1:
        raise ValueError("rows must be positive")
    generate(args.rows, args.output, args.seed)


if __name__ == "__main__":
    main()
