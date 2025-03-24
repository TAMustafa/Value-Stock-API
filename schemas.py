from pydantic import BaseModel
from typing import Optional

class YahooDataSchema(BaseModel):
    symbol: str
    name: str
    last_price: float
    target_price_low: Optional[float]
    difference_low: Optional[float]
    target_price_median: Optional[float]
    difference_median: Optional[float]
    target_price_high: Optional[float]
    difference_high: Optional[float]
    volume_numeric: Optional[float]
    volume_str: Optional[str]
    market_cap: Optional[float]
    pb_ratio: Optional[float]
    short_interest: Optional[float]

    class Config:
        from_attributes = True
