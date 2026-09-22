import csv
from src.generate_data import generate


def test_generate_data(tmp_path):
    output = tmp_path / "orders.csv"
    generate(25, str(output), seed=7)
    with output.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    assert len(rows) == 26
    assert rows[0][0] == "order_id"
