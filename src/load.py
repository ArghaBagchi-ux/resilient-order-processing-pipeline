import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.db.connection import get_connection

RETRY_POLICY = dict(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)


@retry(**RETRY_POLICY)
def upsert_orders(orders, source_file):
    rows = list(orders)
    if not rows:
        return 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for order in rows:
                cur.execute("""
                    INSERT INTO orders
                    (order_id, customer_id, product_id, country, quantity,
                     unit_price, status, order_ts, source_file, loaded_at, updated_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
                    ON CONFLICT (order_id) DO UPDATE SET
                      customer_id=EXCLUDED.customer_id,
                      product_id=EXCLUDED.product_id,
                      country=EXCLUDED.country,
                      quantity=EXCLUDED.quantity,
                      unit_price=EXCLUDED.unit_price,
                      status=EXCLUDED.status,
                      order_ts=EXCLUDED.order_ts,
                      source_file=EXCLUDED.source_file,
                      updated_at=NOW()
                """, (order.order_id, order.customer_id, order.product_id,
                      order.country, order.quantity, order.unit_price,
                      order.status, order.order_ts, source_file))
        conn.commit()
    return len(rows)


@retry(**RETRY_POLICY)
def load_dead_letters(records, source_file):
    if not records:
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            for item in records:
                cur.execute("""
                    INSERT INTO dead_letter_orders
                    (source_file, source_line, raw_payload, error_reason)
                    VALUES (%s,%s,%s::jsonb,%s)
                """, (source_file, item["line"],
                      json.dumps(item["payload"], default=str), item["error"]))
        conn.commit()


@retry(**RETRY_POLICY)
def start_run(run_id, source_file, started_at):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pipeline_runs(run_id, source_file, started_at, status)
                VALUES (%s,%s,%s,'RUNNING')
            """, (str(run_id), source_file, started_at))
        conn.commit()


@retry(**RETRY_POLICY)
def finish_run(run_id, status, metrics, finished_at, error_message=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pipeline_runs
                SET finished_at=%s,status=%s,records_read=%s,
                    records_valid=%s,records_loaded=%s,
                    records_rejected=%s,error_message=%s
                WHERE run_id=%s
            """, (finished_at, status, metrics["read"], metrics["valid"],
                  metrics["loaded"], metrics["rejected"], error_message, str(run_id)))
        conn.commit()
