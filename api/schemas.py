from pydantic import BaseModel

class TransactionRequest(BaseModel):
    account_id: str
    amount: float
    type: int