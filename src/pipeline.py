import argparse
import logging
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from src.load import finish_run, load_dead_letters, start_run, upsert_orders
from src.transform import validate_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(processName)s | %(message)s",
)
logger = logging.getLogger(__name__)


def process_record(item):
    line, payload = item
    order, error = validate_record(payload)
    return line, order, error, payload


def run_pipeline(input_file: str, workers: int = 4, chunk_size: int = 5000):
    run_id = uuid4()
    started = datetime.now(timezone.utc)
    start_run(run_id, input_file, started)
    metrics = {"read": 0, "valid": 0, "loaded": 0, "rejected": 0}

    try:
        for chunk_number, chunk in enumerate(
            pd.read_csv(input_file, chunksize=chunk_size), start=1
        ):
            logger.info("run_id=%s chunk=%s rows=%s", run_id, chunk_number, len(chunk))
            metrics["read"] += len(chunk)
            records = [(int(i) + 2, row.to_dict()) for i, row in chunk.iterrows()]
            valid, bad = [], []

            with ProcessPoolExecutor(max_workers=workers) as pool:
                for line, order, error, payload in pool.map(process_record, records):
                    if error:
                        metrics["rejected"] += 1
                        bad.append({"line": line, "payload": payload, "error": error})
                    else:
                        metrics["valid"] += 1
                        valid.append(order)

            load_dead_letters(bad, input_file)
            metrics["loaded"] += upsert_orders(valid, input_file)

        finish_run(run_id, "SUCCESS", metrics, datetime.now(timezone.utc))
        logger.info("Pipeline completed: %s", metrics)
        return metrics
    except Exception as exc:
        logger.exception("Pipeline failed")
        try:
            finish_run(run_id, "FAILED", metrics, datetime.now(timezone.utc), str(exc))
        except Exception:
            logger.exception("Could not update pipeline audit record")
        raise


def main():
    parser = argparse.ArgumentParser(description="Run the resilient order pipeline")
    parser.add_argument("--input", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--chunk-size", type=int, default=5000)
    args = parser.parse_args()
    if args.workers < 1 or args.chunk_size < 1:
        raise ValueError("workers and chunk-size must be positive")
    if not Path(args.input).exists():
        raise FileNotFoundError(args.input)
    run_pipeline(args.input, args.workers, args.chunk_size)


if __name__ == "__main__":
    main()
