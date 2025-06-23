from pydantic import BaseModel
from datetime import datetime

class FuturePriceInput(BaseModel):
    time: datetime
    symbol: str
    price: float
