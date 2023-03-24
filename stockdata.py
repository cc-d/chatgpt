#!/usr/bin/env python3
"""
A script to retrieve stock data using the Alpha Vantage API.
"""

import sys
from typing import List, Dict, Union
import requests

BASE_URL = "https://www.alphavantage.co/query"


def read_api_key() -> str:
    """Read the API key from a file named 'av.key'.

    Returns:
        str: The API key.
    """
    with open("av.key", "r") as f:
        return f.read().strip()


API_KEY = read_api_key()


def get_stock_data(symbol: str) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:
    """Retrieve stock data for a given symbol.

    Args:
        symbol (str): The stock symbol to retrieve data for.

    Returns:
        Dict[str, Union[str, Dict[str, Union[str, float]]]]: A dictionary containing the stock data.
    """
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "apikey": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(f"Failed to retrieve stock data for symbol {symbol}")

    data = response.json()

    if "Error Message" in data:
        raise Exception(f"Failed to retrieve stock data for symbol {symbol}")

    return data


def get_stock_close_values(symbol: str, start_date: str, end_date: str) -> List[float]:
    """Retrieve closing stock values for a given symbol and date range.

    Args:
        symbol (str): The stock symbol to retrieve data for.
        start_date (str): The start date for the range in the format YYYY-MM-DD.
        end_date (str): The end date for the range in the format YYYY-MM-DD.

    Returns:
        List[float]: A list of closing stock values.
    """
    data = get_stock_data(symbol)

    time_series_daily = data["Time Series (Daily)"]

    close_values = []
    for date, value in time_series_daily.items():
        if start_date <= date <= end_date:
            close_values.append(float(value["4. close"]))

    return close_values


if __name__ == "__main__":
    symbol = sys.argv[1]
    start_date = '2022-01-01'
    end_date = '2023-12-31'

    close_values = get_stock_close_values(symbol, start_date, end_date)

    print(f"Closing values for {symbol} between {start_date} and {end_date}:")
    print(close_values)

