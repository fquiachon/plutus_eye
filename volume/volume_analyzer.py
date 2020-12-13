from datetime import datetime, timedelta
from ..candle_pattern.gateway import get_data


class VolumeAnalyzer:
    def __init__(self):
        self.quad = []
        self.trip = []
        self.doub = []
        self.single = []
        self.below = []
        self.increased_symbols = {
            "Quadrupled": self.quad,
            "Tripled": self.trip,
            "Doubled": self.doub,
            "Same": self.single,
            "Below": self.below,
            "Status": "Not Started"
        }

    def analyze_many(self, tickers):
        for idx, ticker in enumerate(tickers):
            try:
                ticker = ticker.upper()
                self.analyze(ticker)
            except Exception as e:
                print(e)
            finally:
                self.increased_symbols['Status'] = f'{idx+1}/{len(tickers)} Completed'

    def analyze(self, ticker):
        ticker = ticker.upper()
        end_datetime = datetime.now()
        start_datetime = end_datetime - timedelta(days=15)
        print(f'start: {start_datetime} and end: {end_datetime}')
        result = get_data(ticker, start_datetime.timestamp(), end_datetime.timestamp())
        previous_averaged_volume = int(result['volume'].iloc[0:9].mean())
        todays_volume = result.volume.iloc[-1]
        todays_date = result.trading_date.iloc[-1]
        print(f'current:{todays_volume}, previous:{previous_averaged_volume}')
        self.get_volume_percent(todays_date, previous_averaged_volume, ticker, todays_volume)
        self.increased_symbols['Status'] = 'Completed'
        return self.increased_symbols

    def get_volume_percent(self, todays_date, previous_averaged_volume, ticker, todays_volume):
        if 4 <= (todays_volume / previous_averaged_volume):
            self.quad.append({'symbol': ticker, 'date': todays_date, 'size': f'{(todays_volume / previous_averaged_volume):.2f}'})
        elif 3 <= (todays_volume / previous_averaged_volume):
            self.trip.append({'symbol': ticker, 'date': todays_date, 'size': f'{(todays_volume / previous_averaged_volume):.2f}'})
        elif 2 <= (todays_volume / previous_averaged_volume):
            self.doub.append({'symbol': ticker, 'date': todays_date, 'size': f'{(todays_volume / previous_averaged_volume):.2f}'})
        elif 1 <= (todays_volume / previous_averaged_volume):
            self.single.append({'symbol': ticker, 'date': todays_date, 'size': f'{(todays_volume / previous_averaged_volume):.2f}'})
        else:
            self.below.append({'symbol': ticker, 'date': todays_date, 'size': f'{(todays_volume / previous_averaged_volume):.2f}'})
