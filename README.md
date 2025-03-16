# Undervalued Stocks API

A FastAPI-based application for identifying and analyzing undervalued stocks using Yahoo Finance data and price targets.

## Overview

This project provides an API to analyze stock market data, specifically focusing on identifying potentially undervalued stocks based on their current price compared to analyst price targets. The system fetches data from Yahoo Finance, processes it, and provides various endpoints to query and analyze the results.

## Features

- **Data Collection**: Automatically scrapes Yahoo Finance for trending stocks, gainers, and most active securities
- **Price Target Analysis**: Fetches analyst price targets using the yfinance library
- **Undervalued Stock Detection**: Identifies stocks trading below their analyst price targets
- **Flexible Filtering**: Multiple parameters for filtering results (volume, price range, target price differences)
- **RESTful API**: Clean, well-documented FastAPI endpoints

## Tech Stack

- **FastAPI**: Modern, high-performance web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Pandas**: Data manipulation and analysis
- **yfinance**: Yahoo Finance market data downloader
- **PostgreSQL**: Relational database for data storage

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/undervalued-stocks-api.git
   cd undervalued-stocks-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database:
   ```bash
   # Create a database named yahoo_db
   # Update the database URL in the code if needed
   ```

## Usage

### Running the Data Collection Script

Run the data collection script to fetch and process stock data:

```bash
python main.py
```

This will:
1. Fetch stock data from Yahoo Finance
2. Get analyst price targets
3. Calculate percentage differences
4. Store the results in the PostgreSQL database

### Starting the API Server

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs

### API Endpoints

- `GET /`: Redirects to `/data/`
- `GET /data/`: List all stock data with pagination
- `GET /data/{symbol}`: Get data for a specific stock symbol
- `GET /stats/`: Get basic statistics about stored data
- `GET /undervalued/`: Get undervalued stocks with various filtering options

#### Undervalued Stocks Endpoint

The `/undervalued/` endpoint provides powerful filtering options:

- `limit`: Number of stocks to return (1-20)
- `min_volume`: Filter stocks by minimum trading volume
- `min_price`: Filter stocks by minimum current price
- `max_price`: Filter stocks by maximum current price
- `min_target_diff`: Minimum percentage difference from low target price
- `exclude_above_median`: Exclude stocks trading above their median target price
- `sort_by`: Field to sort results by
- `ascending`: Sort in ascending order instead of descending

Example query:
```
GET /undervalued/?min_volume=1000000&min_price=10&min_target_diff=10&exclude_above_median=true
```

## Database Schema

The main table `yahoo_data` includes the following fields:

- `symbol`: Stock ticker symbol
- `name`: Company name
- `last_price`: Current stock price
- `target_price_low`: Low analyst price target
- `target_price_median`: Median analyst price target
- `target_price_high`: High analyst price target
- `difference_low`: Percentage difference from low target
- `difference_median`: Percentage difference from median target
- `difference_high`: Percentage difference from high target
- `volume_numeric`: Trading volume (numeric)
- `volume_str`: Trading volume (string format)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Disclaimer

This tool is for educational purposes only. Always perform your own research before making investment decisions. The data provided may not be accurate or up-to-date.