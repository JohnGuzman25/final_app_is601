from pydantic import BaseModel, Field
from typing import Literal


class TransactionCreate(BaseModel):
    tx_type: Literal["income", "expense"]
    category: str = Field(min_length=1, max_length=50)
    note: str = Field(default="", max_length=255)
    amount: float
