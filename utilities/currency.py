import requests
from decouple import config

EXCHANGE_RATES_API_KEY = config('EXCHANGE_RATES_API_KEY')
def convert_currencyx(amount, from_currency, to_currency):
    url = f"http://api.exchangeratesapi.io/latest?access_key={EXCHANGE_RATES_API_KEY}&base={from_currency}&symbols={to_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json().get('rates', {})
        conversion_rate = rates.get(to_currency, 0)
        return amount * conversion_rate
    else:
        return None  # or handle error appropriately


import requests
import time


def convert_currency(amount, from_currency, to_currency):
    # Get the current Unix timestamp
    unix_timestamp = int(time.time())

    # Set the default base currency as EUR, which is typically the base for free API plans
    default_base = 'EUR'

    # If the from_currency is not EUR, convert to EUR first
    if from_currency != default_base:
        # Convert from the original currency to EUR
        url = f"http://api.exchangeratesapi.io/latest?access_key={EXCHANGE_RATES_API_KEY}&symbols={default_base}"
        response = requests.get(url)
        if response.status_code == 200 and response.json().get('success', False):
            rates = response.json().get('rates', {})
            from_to_eur_rate = rates.get(default_base, 0)
            if from_currency == 'USD':  # If the original currency is USD
                amount_in_eur = amount / from_to_eur_rate if from_to_eur_rate else 0
            else:
                # Handle other non-EUR base currencies if necessary
                pass
        else:
            return None, unix_timestamp
    else:
        amount_in_eur = amount

    # Now convert from EUR to the target currency
    url = f"http://api.exchangeratesapi.io/latest?access_key={EXCHANGE_RATES_API_KEY}&symbols={to_currency}"
    response = requests.get(url)
    if response.status_code == 200 and response.json().get('success', False):
        rates = response.json().get('rates', {})
        eur_to_target_rate = rates.get(to_currency, 0)
        converted_amount = amount_in_eur * eur_to_target_rate if eur_to_target_rate else 0
        return converted_amount, unix_timestamp
    else:
        return None, unix_timestamp
