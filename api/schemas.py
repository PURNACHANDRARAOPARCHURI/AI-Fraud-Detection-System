from pydantic import BaseModel
class TransactionRequest(BaseModel):
    account_id: int
    amount: float
    type: int