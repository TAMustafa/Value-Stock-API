from sqlalchemy import Column, String, Float, Integer
from database import Base

class YahooData(Base):
    __tablename__ = 'yahoo_data'
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String)
    last_price = Column(Float)
    target_price_low = Column(Float)
    difference_low = Column(Float)
    target_price_median = Column(Float)
    difference_median = Column(Float)
    target_price_high = Column(Float)
    difference_high = Column(Float)
    volume_numeric = Column(Integer)
    volume_str = Column(String(10))
