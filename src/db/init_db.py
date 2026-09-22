from pathlib import Path
from src.db.connection import get_connection


def main():
    schema = Path("sql/schema.sql").read_text(encoding="utf-8")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema)
        conn.commit()
    print("Database schema initialized")


if __name__ == "__main__":
    main()
