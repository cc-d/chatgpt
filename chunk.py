#!/usr/bin/env python3

import json
import sys
from typing import Dict, List, Union


def read_json_file(file_path: str) -> Dict:
    """Reads a JSON file from the given path and returns a dictionary."""
    with open(file_path) as f:
        data = json.load(f)
    return data


def get_monthly_data(stock_data: Dict[str, Dict[str, Union[str, float]]]) -> Dict[str, Dict[str, float]]:
    """Extracts monthly data from the given daily stock data.

    Args:
        stock_data (Dict[str, Dict[str, Union[str, float]]]): A dictionary containing daily stock data.

    Returns:
        Dict[str, Dict[str, float]]: A dictionary containing monthly stock data.
    """
    monthly_data = {}

    for date, values in stock_data["Time Series (Daily)"].items():
        year_month = date[:7]
        if year_month not in monthly_data:
            monthly_data[year_month] = {
                "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0, "volume": 0.0}

        monthly_data[year_month]["open"] += float(values["1. open"])
        monthly_data[year_month]["high"] += float(values["2. high"])
        monthly_data[year_month]["low"] += float(values["3. low"])
        monthly_data[year_month]["close"] += float(values["4. close"])
        monthly_data[year_month]["volume"] += float(values["6. volume"])

    for year_month, values in monthly_data.items():
        values["open"] /= 20  # average of 20 days
        values["high"] /= 20  # average of 20 days
        values["low"] /= 20  # average of 20 days
        values["close"] /= 20  # average of 20 days
        values["volume"] /= 20  # average of 20 days

    return monthly_data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_stock_data.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # read stock data from file
    with open(file_path) as f:
        stock_data = json.load(f)

    monthly_data = get_monthly_data(stock_data)

    print("Monthly Stock Data")
    for year_month, values in monthly_data.items():
        print(year_month, values)
