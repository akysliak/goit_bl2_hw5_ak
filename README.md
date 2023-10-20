Required package: aiohttp.

To run with default parameters (date: today, currencies: EUR, USD), use the following command:

    python main.py

To provide a required range of dates (0-10 days back from the current date):

    python main.py <n_days>

where <n_days> is an integer between 0 and 10.

To specify additional currencies:

    python main.py <n_days> <currency_list>

where <currency_list> is a list of currencies, separated with empty spaces. E.g.:

    python main.py 4 CHF GBP PLZ XAU  
