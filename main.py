import platform

import aiohttp
import asyncio
import json
import logging
import sys

from datetime import date, timedelta

REQUEST_URL = "https://api.privatbank.ua/p24api/exchange_rates?date="


def date_to_str(tgt_date: date):
    return tgt_date.strftime('%d.%m.%Y')


def get_tgt_dates_from_input():
    today = date.today()
    tgt_dates = [date_to_str(today)]
    if len(sys.argv) > 1:
        try:
            n_days = int(sys.argv[1])
            if n_days > 10 or n_days < 0:
                raise ValueError
            while n_days > 0:
                tgt_dates.append(date_to_str(today - timedelta(n_days)))
                n_days -= 1
        except ValueError:
            logging.info(f"Input '{sys.argv[1]}' is not a valid number of days (will be ignored). "
                  f"Possible numbers are 0 to 10.")
    return tgt_dates


def get_tgt_currencies_from_input():
    currencies = {"EUR", "USD"}
    if len(sys.argv) > 2:
        currencies.update(sys.argv[2:])
    return currencies


def parse_response(response, tgt_currencies=["EUR", "USD"]):
    tgt_date = response["date"]
    res = {}
    currencies_info = response["exchangeRate"]
    for currency_info in currencies_info:
        if currency_info["currency"] in tgt_currencies:
            res[currency_info["currency"]] = {
                'sale': currency_info["saleRate"] if "saleRate" in currency_info else "not sold by PB",
                'purchase': currency_info["purchaseRate"] if "purchaseRate" in currency_info else "not purchased by PB"
            }
    return {tgt_date: res}


async def send_requests(tgt_dates, tgt_currencies=["EUR", "USD"]):
    result = []
    async with aiohttp.ClientSession() as session:
        for tgt_date in tgt_dates:
            url = f'{REQUEST_URL}{tgt_date}'
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        response = await response.json()
                        response = parse_response(response, tgt_currencies)
                        result.append(response)
                    else:
                        logging.info(f"Error status: {response.status}, for date: {tgt_date}.")
            except (aiohttp.ClientConnectorError, aiohttp.InvalidURL) as err:
                logging.info(f"Connection error: {url}, {str(err)}")
    return result


def reformat_result(result):
    result = sorted(result, key=lambda x: next(iter(x.keys())), reverse=True)
    result = json.dumps(result, indent=4)
    return result


async def main():
    tgt_dates = get_tgt_dates_from_input()
    logging.info(f"The following date(s) will be considered: {tgt_dates}")
    tgt_currencies = get_tgt_currencies_from_input()
    logging.info(f"The following currencies will be considered if available: {tgt_currencies}")
    result = await send_requests(tgt_dates, tgt_currencies)
    result = reformat_result(result)
    print(result)
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())