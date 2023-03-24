#!/usr/bin/env python3
"""
A script to retrieve stock and financial data using the Alpha Vantage API.
"""

import sys
import json
from typing import Dict, Union
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


def get_financial_data(function: str, symbol: str) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:
    """Retrieve financial data for a given symbol and function.

    Args:
        function (str): The Alpha Vantage API function to use.
        symbol (str): The stock symbol to retrieve data for.

    Returns:
        Dict[str, Union[str, Dict[str, Union[str, float]]]]: A dictionary containing the financial data.
    """
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": API_KEY,
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to retrieve financial data for symbol {symbol}")

    data = response.json()

    if "Error Message" in data:
        raise Exception(
            f"Failed to retrieve financial data for symbol {symbol}")

    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python financial_data.py SYMBOL")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    functions = ["TIME_SERIES_DAILY_ADJUSTED", "BALANCE_SHEET",
                 "CASH_FLOW", "INCOME_STATEMENT", "OVERVIEW"]

    financial_data = {}

    for function in functions:
        financial_data[function] = get_financial_data(function, symbol)

    # Filter time-series data to the specified date range
    time_series = financial_data["TIME_SERIES_DAILY_ADJUSTED"]["Time Series (Daily)"]
    filtered_time_series = {date: values for date, values in time_series.items(
    ) if "2022-01-01" <= date <= "2023-12-31"}
    financial_data["TIME_SERIES_DAILY_ADJUSTED"]["Time Series (Daily)"] = filtered_time_series

    # Save the financial data to a file named "$stockName.stock"
    with open(f"{symbol}.json", "w") as f:
        json.dump(financial_data, f, indent=2)

    print(f"Financial data for {symbol} saved to {symbol}.stock")
