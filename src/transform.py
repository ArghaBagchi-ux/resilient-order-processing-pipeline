from pydantic import ValidationError
from src.models import Order

REQUIRED_COLUMNS = {
    "order_id", "customer_id", "product_id", "country",
    "quantity", "unit_price", "status", "order_ts"
}


def validate_record(payload: dict):
    try:
        missing = REQUIRED_COLUMNS - payload.keys()
        if missing:
            raise ValueError(f"missing columns: {sorted(missing)}")
        return Order.model_validate(payload), None
    except (ValidationError, ValueError, TypeError) as exc:
        return None, str(exc)
