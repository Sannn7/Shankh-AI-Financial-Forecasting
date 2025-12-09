from pydantic import BaseModel
from typing import List, Optional




class StockRequest(BaseModel):
    ticker: str
    period: Optional[str] = '1y'
    interval: Optional[str] = '1d'

class Ticker(BaseModel):
    ticker:str