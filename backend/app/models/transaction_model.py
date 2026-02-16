from pydantic import BaseModel

class Transaction(BaseModel):
    tx_id: str
    amount: float
    currency: str
    timestamp: str
    from_account: str
    to_account: str
