import requests
import pandas as pd


class PseAPI:

    def get_data(self, ticker, start_date, end_date):
        ticker = ticker.upper()
        try:
            latest = requests.get(f'http://phisix-api.appspot.com/stocks/{ticker}.json', timeout=10).json()
            last_price = latest['stock'][0]['price']['amount']
            my_request = f'https://pselookup.vrymel.com/api/stocks/{ticker}/history/{start_date}/{end_date}'
            print(my_request)
            data = requests.get(my_request, timeout=10).json()[
                'history']
            data[-1]['close'] = last_price
            return pd.json_normalize(data)
        except Exception as e:
            raise Exception(f'Error occurred while processing {ticker}, {e}')
