from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class PriceOverrideRequest(BaseModel):
    type: Literal["crypto", "forex", "gold"]
    symbol: Optional[str] = None
    type_gold: Optional[str] = None
    datetime: datetime
    custom_price: float
    id_user: Optional[int] = None
