import pandas as pd
import requests
import yfinance as yf
from io import StringIO
from sqlalchemy import create_engine

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
SECTIONS = ["gainers", "most-active", "trending-tickers"]
COLUMNS_TO_KEEP = ['Symbol', 'Name', 'Price', 'Volume']
DB_URL = "postgresql://postgres:postgres@localhost:5432/yahoo_db"

def save_to_postgres(df, table_name="yahoo_data"):
    """Saves DataFrame to a PostgreSQL database."""
    engine = create_engine(DB_URL)
    with engine.connect() as connection:
        df.to_sql(table_name, connection, if_exists='replace', index=False)

def fetch_yahoo_data():
    """Fetches data from Yahoo Finance for specified sections."""
    combined_data = []
    for section in SECTIONS:
        url = f"https://finance.yahoo.com/markets/stocks/{section}/"
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching {section}: {e}")
            continue
        tables = pd.read_html(StringIO(response.text))
        if tables:
            df = tables[0]
            if set(COLUMNS_TO_KEEP).issubset(df.columns):
                combined_data.append(df[COLUMNS_TO_KEEP])
    return pd.concat(combined_data, ignore_index=True).drop_duplicates(subset='Symbol') if combined_data else pd.DataFrame()

def fetch_stock_metrics(symbols):
    """Fetches fundamental stock metrics from Yahoo Finance."""
    tickers = yf.Tickers(" ".join(symbols))
    results = []
    for symbol in symbols:
        ticker = tickers.tickers.get(symbol, None)
        if ticker:
            info = ticker.info
            results.append({
                "Symbol": symbol,
                "market_cap": info.get("marketCap"),
                "pb_ratio": info.get("priceToBook"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "short_interest": info.get("shortPercentOfFloat"),
            })
    return pd.DataFrame(results)

def fetch_price_target(symbols):
    """Fetches price targets from Yahoo Finance."""
    tickers = yf.Tickers(" ".join(symbols))
    results = []
    for symbol in symbols:
        ticker = tickers.tickers.get(symbol, None)
        if ticker and hasattr(ticker, "analyst_price_targets"):
            targets = ticker.analyst_price_targets or {}
            results.append({
                "Symbol": symbol,
                "target_price_low": targets.get("low"),
                "target_price_median": targets.get("median"),
                "target_price_high": targets.get("high")
            })
    return pd.DataFrame(results)

def clean_price_column(df):
    """Extracts numeric price from 'Price' column."""
    df['last'] = pd.to_numeric(df['Price'].str.extract(r'([\d.]+)')[0], errors='coerce')
    return df.drop(columns=['Price'])

def clean_volume_column(df):
    """Converts volume strings to numeric values."""
    volume_str = df['Volume'].copy()
    volume_str = volume_str.str.replace('M', 'e6').str.replace('K', 'e3')
    df['volume_numeric'] = pd.to_numeric(volume_str, errors='coerce')
    return df

def calculate_percentage_differences(df):
    """Calculates percentage differences between current price and targets."""
    for target in ['target_price_low', 'target_price_median', 'target_price_high']:
        df[f'%_{target}'] = ((df[target] - df['last']) / df['last'] * 100).round(2)
    return df

def merge_and_calculate():
    """Merges Yahoo data, price targets, and stock metrics."""
    yahoo_data = fetch_yahoo_data()
    if yahoo_data.empty:
        print("No data fetched from Yahoo Finance.")
        return
    symbols = yahoo_data['Symbol'].tolist()
    price_targets = fetch_price_target(symbols)
    stock_metrics = fetch_stock_metrics(symbols)
    merged_data = pd.merge(yahoo_data, price_targets, on='Symbol', how='inner')
    merged_data = pd.merge(merged_data, stock_metrics, on='Symbol', how='left')
    cleaned_data = clean_price_column(merged_data)
    cleaned_data = clean_volume_column(cleaned_data)
    final_data = calculate_percentage_differences(cleaned_data)
    final_data = final_data.rename(columns={
        'Symbol': 'symbol',
        'Name': 'name',
        'last': 'last_price',
        '%_target_price_low': 'difference_low',
        '%_target_price_median': 'difference_median',
        '%_target_price_high': 'difference_high',
        'Volume': 'volume_str',
    })
    save_to_postgres(final_data)

if __name__ == "__main__":
    merge_and_calculate()