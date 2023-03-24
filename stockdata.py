#!/usr/bin/env python3

"""
A script to retrieve stock and financial data using the Alpha Vantage API and write
monthly averages of financial data values to a json file.
"""

import sys
from json import dumps, loads
from typing import Dict, Union
from datetime import datetime
import requests
from time import sleep
from myutils import logf, mlogger
import os

CURPATH = os.path.abspath(os.path.dirname(__file__))

BASE_URL = "https://www.alphavantage.co/query"
SLEEPFOR = 15
HALFSFOR = SLEEPFOR / 2

ESTR = 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call frequency.'


@logf()
def msleep(sfor=SLEEPFOR):
    remaining = float(str(sfor))
    while remaining > 0:
        msg = f'{remaining} time remaining...'
        sleep(1)
        mlogger.debug(msg)
        remaining -= 1
    return sfor


@logf()
def read_api_key() -> str:
    """Read the API key from a file named 'av.key'.

    Returns:
        str: The API key.
    """
    with open("av.key", "r") as f:
        return f.read().strip()


API_KEY = read_api_key()

SKIPSLEEP = True

class Sfor:
    def __enter__(self):
        global SKIPSLEEP
        if not SKIPSLEEP:
            msleep()
        else:
            mlogger.debug(f'SKIPSLEEP={SKIPSLEEP} SKIPPING')
            SKIPSLEEP = False
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        mlogger.debug("FINISHED Sfor")


@logf(level='info')
def rget(BASE_URL, params):
    symb, func = params['symbol'], params['function']
    def get_resp(BASE_URL, params):
        with Sfor():
            return requests.get(BASE_URL, params=params)

    try:
        resp = get_resp(BASE_URL, params)
        if resp.status_code != 200:
            mlogger(f'first resp status_code not 200 retrying')
            with Sfor():
                resp = get_resp(BASE_URL, params)
    except Exception as e:
        mlogger.debug(f'rget resp execption {e} retrying')
        with Sfor():
            resp = get_resp(BASE_URL, params)

    if resp.status_code == 200:
        mlogger.debug('good status code')
        return resp
    else:
        mlogger.debug('bad status code @@')



@logf(level='info')
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
    return rget(BASE_URL, params)


@logf()
def get_monthly_data(stock_data: Dict[str, Union[str, Dict[str, Union[str, float]]]]) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:

    time_series_data = {}
    monthly_data = {}

    for function in stock_data:
        if function == "Meta Data":
            continue

        time_series_data[function] = stock_data[function].get(
            f"{function}", {})
        for date, values in time_series_data[function].items():
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            month = date_obj.strftime("%Y-%m")

            if month not in monthly_data:
                monthly_data[month] = {}

            for key, value in values.items():
                try:
                    float_value = float(value)
                except ValueError:
                    continue

                if key not in monthly_data[month]:
                    monthly_data[month][key] = 0.0
                monthly_data[month][key] += float_value

    for month in monthly_data:
        for key in monthly_data[month]:
            monthly_data[month][key] = round(monthly_data[month][key] / 22, 2)

    return {"Monthly Data": monthly_data}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        mlogger.debug("Usage: python financial_data.py SYMBOL")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    DPATH = os.path.join(CURPATH, symbol)
    if not os.path.isdir(DPATH):
        mlogger.debug(f'dir {DPATH} doesnt exist creating now...')
        os.mkdir(DPATH)

    functions = [
        "OVERVIEW",
        "INCOME_STATEMENT",
        "BALANCE_SHEET",
        "CASH_FLOW",
        "EARNINGS",
        "EPS",
        "FINANCIALS",
        "LISTING_STATUS",
        "SECTOR",
        "RATING",
        "GROWTH",
        "INSIDER",
        "INSTITUTIONAL",
        "RECOMMENDATION",
        "HISTORICAL_DATA",
    ]

    financial_data = {}
    for function in functions:
        try:
            fdata = get_financial_data(function, symbol).text

            financial_data[function] = fdata
            fname = f'{function}.json'
            fpath = os.path.join(DPATH, fname)

            if os.path.exists(fpath):
                mlogger.debug(f'fpath {fpath} exists overwriting...')
            else:
                mlogger.debug(f'fpath {fpath} does not exist, creating...')

            with open(fpath, 'w+') as f:
                f.write(fdata)

        except Exception as e:
            mlogger.debug(f"Failed to retrieve data for {function}: {e}")

    monthly_data = get_monthly_data(financial_data) 

    with open(os.path.join(CURPATH, 'monthly.json'), "w") as f:
        f.write(dumps(monthly_data))

    mlogger.debug(f"Monthly data for {symbol} has been written to {symbol}.json")
