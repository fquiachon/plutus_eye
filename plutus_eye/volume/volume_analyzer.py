class VolumeAnalyzer:
    def __init__(self, gateway, history):
        self.history = history
        self.gateway = gateway
        self.single = {}
        self.below = {}
        self.quad_summary = []
        self.trip_summary = []
        self.doub_summary = []
        self.quad = {'tickers': self.quad_summary}
        self.trip = {'tickers': self.trip_summary}
        self.doub = {'tickers': self.doub_summary}
        self.increased_symbols = {
            "Quadrupled": self.quad,
            "Tripled": self.trip,
            "Doubled": self.doub,
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
                self.increased_symbols['In average'] = f'{len(self.single)} Stocks'
                self.increased_symbols['Below average'] = f'{len(self.below)} Stocks'

    def analyze(self, ticker):
        ticker = ticker.upper()
        start, end = self.history.get_range(days=20)
        try:
            result = self.gateway.get_data(ticker, start, end)
        except Exception as e:
            print(e)
            return {'error': f'{e}'}

        previous_averaged_volume = int(result['volume'].iloc[0:9].mean())
        todays_volume = result.volume.iloc[-1]
        todays_date = result.trading_date.iloc[-1]
        todays_open = result.open.iloc[-1]
        todays_close = result.close.iloc[-1]
        candle = 'Bull' if (todays_close > todays_open) else 'Bear'

        print(f'current:{todays_volume}, previous:{previous_averaged_volume}')
        self.get_volume_percent(todays_date, previous_averaged_volume, ticker, todays_volume, candle, todays_close)
        self.increased_symbols['Status'] = 'Completed'
        self.increased_symbols['In average'] = f'{len(self.single)} Stocks' if len(self.single) != 0 else []
        self.increased_symbols['Below average'] = f'{len(self.below)} Stocks' if len(self.below) != 0 else []
        return self.increased_symbols

    def get_volume_percent(self, todays_date, previous_averaged_volume, ticker, todays_volume, candle, todays_close):
        if 4 <= (todays_volume / previous_averaged_volume):
            self.quad[ticker] = {'date': todays_date,
                                       'size': f'{(todays_volume / previous_averaged_volume):.2f}',
                                       'price': f'{todays_close:.2f}',
                                       'candle': candle,
                                       'link': f'https://www.investagrams.com/Chart/{ticker}'
                                  }
            self.quad_summary.append(ticker)
        elif 3 <= (todays_volume / previous_averaged_volume):
            self.trip[ticker] = {'date': todays_date,
                                       'size': f'{(todays_volume / previous_averaged_volume):.2f}',
                                       'price': f'{todays_close:.2f}',
                                       'link': f'https://www.investagrams.com/Chart/{ticker}',
                                       'candle': candle
                                       }
            self.trip_summary.append(ticker)
        elif 2 <= (todays_volume / previous_averaged_volume):
            self.doub[ticker] = {'date': todays_date,
                                       'size': f'{(todays_volume / previous_averaged_volume):.2f}',
                                       'price': f'{todays_close:.2f}',
                                       'link': f'https://www.investagrams.com/Chart/{ticker}',
                                       'candle': candle
                                       }
            self.doub_summary.append(ticker)
        elif 1 <= (todays_volume / previous_averaged_volume):
            self.single[ticker] = {'date': todays_date,
                                         'size': f'{(todays_volume / previous_averaged_volume):.2f}',
                                         'price': f'{todays_close:.2f}',
                                         'link': f'https://www.investagrams.com/Chart/{ticker}',
                                         'candle': candle
                                         }
        else:
            self.below[ticker] = {'date': todays_date,
                                  'size': f'{(todays_volume / previous_averaged_volume):.2f}',
                                  'price': f'{todays_close:.2f}',
                                  'candle': candle
                                  }
