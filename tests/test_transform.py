from src.transform import validate_record


def valid_payload():
    return {
        "order_id": 1,
        "customer_id": 10,
        "product_id": 20,
        "country": "in",
        "quantity": 2,
        "unit_price": "99.50",
        "status": "completed",
        "order_ts": "2026-01-01T10:00:00+00:00",
    }


def test_valid_record():
    order, error = validate_record(valid_payload())
    assert error is None
    assert order.country == "IN"
    assert order.quantity == 2


def test_negative_quantity_is_rejected():
    payload = valid_payload()
    payload["quantity"] = -1
    order, error = validate_record(payload)
    assert order is None
    assert error


def test_invalid_status_is_rejected():
    payload = valid_payload()
    payload["status"] = "unknown"
    order, error = validate_record(payload)
    assert order is None
    assert error


def test_missing_column_is_rejected():
    payload = valid_payload()
    payload.pop("customer_id")
    order, error = validate_record(payload)
    assert order is None
    assert "missing columns" in error
