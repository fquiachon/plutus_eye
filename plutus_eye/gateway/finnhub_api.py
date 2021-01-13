import requests
import pandas as pd
from datetime import datetime, timedelta
from plutus_eye.settings import GATEWAY_TOKEN


class FinnhubAPI:


    def get_data(self, ticker, start_date, end_date):
        ticker = ticker.upper()
        try:
            print(datetime.fromtimestamp(int(start_date)).strftime('%Y-%m-%d'))
            print(datetime.fromtimestamp(int(end_date)).strftime('%Y-%m-%d'))
            print(f'looking up for {ticker}...')
            my_request = f'https://finnhub.io/api/v1/stock/candle?symbol={ticker}' \
                         f'&resolution=D&from={int(start_date)}&to={int(end_date)}&token={GATEWAY_TOKEN}'
            print(my_request)
            data = requests.get(my_request, timeout=10).json()
        except Exception as e:
            raise Exception(f'Error occurred while processing {ticker}, {e}')

        if 'error' in data:
            raise Exception(f'{data["error"]}, {ticker}')
        elif data['s'] != 'ok':
            raise Exception(f'{data["s"]}, {ticker}')

        data.pop('s')

        data['trading_date'] = [datetime.fromtimestamp(tm).strftime('%Y-%m-%d') for tm in data.pop('t')]
        data['close'] = data.pop('c')
        data['low'] = data.pop('l')
        data['high'] = data.pop('h')
        data['open'] = data.pop('o')
        data['volume'] = data.pop('v')

        new_data = []

        for i in range(len(data['close'])):
            new_data.append({x: data[x][i] for x in data})

        return pd.json_normalize(new_data)
