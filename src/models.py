from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

ALLOWED_STATUSES = {"completed", "pending", "cancelled"}


class Order(BaseModel):
    order_id: int
    customer_id: int
    product_id: int
    country: str = Field(min_length=2, max_length=2)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    status: str
    order_ts: datetime

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported status: {value}")
        return value
