from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from typing import List, Optional

from database import SessionLocal, engine
from models import YahooData, Base
from schemas import YahooDataSchema

app = FastAPI(
    title="Undervalued Stock's API",
    description="API for retrieving Yahoo Finance stock data and price targets",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add a root endpoint that redirects to /data/
@app.get("/")
async def root():
    """Redirect to the data endpoint."""
    return RedirectResponse(url="/data/")

@app.get("/data/", response_model=List[YahooDataSchema], tags=["Data"])
async def read_data(
        skip: int = Query(0, description="Number of records to skip"),
        limit: int = Query(100, description="Number of records to return"),
        min_volume: Optional[int] = Query(None, description="Filter by minimum volume"),
        db: Session = Depends(get_db)
):
    """Retrieve stock data with optional filtering and pagination."""
    try:
        query = db.query(YahooData)

        if min_volume is not None:
            query = query.filter(YahooData.volume_numeric >= min_volume)

        return query.offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/{symbol}", response_model=YahooDataSchema, tags=["Data"])
async def read_stock_data(symbol: str, db: Session = Depends(get_db)):
    """Retrieve stock data for a specific symbol."""
    try:
        stock = db.query(YahooData).filter(YahooData.symbol == symbol.upper()).first()
        if stock is None:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        return stock
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/", tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get basic statistics about the stored data."""
    try:
        total_stocks = db.query(YahooData).count()
        avg_volume = db.query(func.avg(YahooData.volume_numeric)).scalar()
        return {
            "total_stocks": total_stocks,
            "average_volume": int(avg_volume) if avg_volume else 0
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/undervalued/", response_model=List[YahooDataSchema], tags=["Analysis"])
async def get_undervalued_stocks(
        limit: int = Query(5, description="Number of stocks to return", ge=1, le=20),
        min_volume: Optional[int] = Query(None, description="Minimum trading volume", ge=0),
        min_price: Optional[float] = Query(None, description="Minimum current price", ge=0),
        max_price: Optional[float] = Query(None, description="Maximum current price", ge=0),
        min_target_diff: Optional[float] = Query(None, description="Minimum difference from low target in percent",
                                                 ge=0),
        exclude_above_median: bool = Query(False, description="Exclude stocks trading above median target"),
        sort_by: str = Query(
            "difference_low",
            description="Sort criterion",
            enum=["difference_low", "difference_median", "difference_high", "volume_numeric", "last_price"]
        ),
        ascending: bool = Query(False, description="Sort in ascending order"),
        db: Session = Depends(get_db)
):
    """Get undervalued stocks with various filtering options.

    Parameters:
    - limit: Number of stocks to return (1-20)
    - min_volume: Filter stocks by minimum trading volume
    - min_price: Filter stocks by minimum current price
    - max_price: Filter stocks by maximum current price
    - min_target_diff: Minimum percentage difference from low target price
    - exclude_above_median: Exclude stocks trading above their median target price
    - sort_by: Field to sort results by
    - ascending: Sort in ascending order instead of descending
    """
    try:
        # Start with base query
        query = db.query(YahooData).filter(YahooData.difference_low.isnot(None))

        # Apply filters
        if min_volume is not None:
            query = query.filter(YahooData.volume_numeric >= min_volume)

        if min_price is not None:
            query = query.filter(YahooData.last_price >= min_price)

        if max_price is not None:
            query = query.filter(YahooData.last_price <= max_price)

        if min_target_diff is not None:
            query = query.filter(YahooData.difference_low >= min_target_diff)

        if exclude_above_median:
            query = query.filter(YahooData.difference_median >= 0)

        # Apply sorting
        sort_column = getattr(YahooData, sort_by)
        query = query.order_by(sort_column.asc() if ascending else sort_column.desc())

        # Get results
        stocks = query.limit(limit).all()

        if not stocks:
            raise HTTPException(
                status_code=404,
                detail="No stocks found matching the specified criteria"
            )

        return stocks
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
