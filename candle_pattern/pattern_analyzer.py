from .gateway import get_data


class PatternAnalyzer:
    def __init__(self):
        self.matched = False
        self.bullish_eng_codes = []
        self.bearish_eng_codes = []
        self.bullish_swing_codes = []
        self.bearish_swing_codes = []

        self.bullish_pinbar = []
        self.bearish_pinbar = []
        self.outside_bar = []
        self.inside_bar = []
        self.bull_hammer = []
        self.bear_hammer = []
        self.gravestone_doji = []
        self.dragonfly_doji = []
        self.doji = []
        self.no_patter = []

        self.patterns = {
            "Status": "1/1 Completed",
            'Bullish Hammer': self.bull_hammer,
            'Bearish Hammer': self.bear_hammer,
            'Bullish Engulfing': self.bullish_eng_codes,
            'Bearish Engulfing': self.bearish_eng_codes,
            'Bullish Pinbar': self.bullish_pinbar,
            'Bearish Pinbar': self.bearish_pinbar,
            'Bullish Swing': self.bullish_swing_codes,
            'Bearish Swing': self.bearish_swing_codes,
            'Doji': self.doji,
            'Butterfly Doji': self.dragonfly_doji,
            'Gravestone Doji': self.gravestone_doji,
            'Outside Bar': self.outside_bar,
            'Inside Bar': self.inside_bar,
            'No Pattern': self.no_patter,
        }

    def analyze_many(self, tickers):
        for idx, ticker in enumerate(tickers):
            try:
                ticker = ticker.upper()
                self.analyze(ticker)
            except Exception as e:
                print(e)
            finally:
                self.patterns['Status'] = f'{idx+1}/{len(tickers)} Completed'

    def analyze(self, ticker, market_type='global'):
        ticker = ticker.upper()
        if market_type == 'global':
            candle_data = get_data(ticker)
            if 's' in candle_data:
                return candle_data
        else:
            candle_data = {'Message': 'Not yet supported'}
            return candle_data

        return self.check_pattern(ticker, candle_data)

    def check_pattern(self, ticker, candle_data):
        self.matched = False
        try:
            if candle_data.shape[0] < 3:
                raise Exception(f'cannot analyze data, adjust start date, {candle_data}')
            for i in range(2, candle_data.shape[0]):
                current = candle_data.iloc[i, :]
                prev = candle_data.iloc[i - 1, :]
                prev_2 = candle_data.iloc[i - 2, :]

                if current['open'] + current['close'] + current['low'] + current['high'] == 0:
                    self.no_patter.append(f'{ticker}:{current.trading_date}')
                    continue
                elif current['open'] < current['close']:
                    candle_type = 'Bull'
                    head_wick = current['high'] - current['close']
                    tail_wick = current['open'] - current['low']
                elif current['open'] > current['close']:
                    candle_type = 'Bear'
                    head_wick = current['high'] - current['open']
                    tail_wick = current['close'] - current['low']
                else:
                    candle_type = 'Doji'
                    head_wick, tail_wick = self.is_doji(current, ticker)

                realbody = abs(current['open'] - current['close'])
                candle_range = current['high'] - current['low']

                # Bullish Engulfing
                self.is_bullish_engulfing(candle_range, current, prev, realbody, ticker)

                # Bearish Engulfing
                self.is_bearish_engulfing(candle_range, current, prev, realbody, ticker)

                # Bullish Swing
                self.is_bullish_swing(current, prev, prev_2, ticker)

                # Bearish Swing
                self.is_bearish_swing(current, prev, prev_2, ticker)

                # Bullish Pinbar
                self.is_bullish_pinbar(candle_range, current, prev, realbody, ticker)

                # Bearish Pinbar
                self.is_bearish_pinbar(candle_range, current, prev, realbody, ticker)

                # Inside bar
                self.is_inside_bar(current, prev, ticker)

                # Outside bar
                self.is_outside_bar(current, prev, ticker)

                # Hammer
                self.is_hammer(candle_type, current, head_wick, realbody, tail_wick, ticker)

                if not self.matched:
                    self.no_patter.append(f'{ticker}:{current.trading_date}')

            return self.patterns
        except Exception as e:
            raise Exception(f'Error for code {ticker}, {candle_data}, {e}')

    def is_doji(self, current, ticker):
        if current['open'] == current['low']:
            self.gravestone_doji.append(f'{ticker}:{current.trading_date}')
            head_wick = current['high'] - current['open']
            tail_wick = 0
        elif current['open'] == current['high']:
            self.dragonfly_doji.append(f'{ticker}:{current.trading_date}')
            head_wick = 0
            tail_wick = current['open'] - current['low']
        else:
            self.doji.append(f'{ticker}:{current.trading_date}')
            tail_wick = current['open'] - current['low']
            head_wick = current['high'] - current['open']
        self.matched = True
        return head_wick, tail_wick

    def is_hammer(self, candle_type, current, head_wick, realbody, tail_wick, ticker):
        if realbody > head_wick * 2 and tail_wick > head_wick * 2 and realbody * 2 < tail_wick:
            if candle_type == 'Bull':
                self.bull_hammer.append(f'{ticker}:{current.trading_date}')
            elif candle_type == 'Bear':
                print(f'{ticker}:{current.trading_date}')
                self.bear_hammer.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_outside_bar(self, current, prev, ticker):
        if current['high'] > prev['high'] and current['low'] < prev['low']:
            self.outside_bar.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_inside_bar(self, current, prev, ticker):
        if current['high'] < prev['high'] and current['low'] > prev['low']:
            self.inside_bar.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_bearish_pinbar(self, candle_range, current, prev, realbody, ticker):
        if realbody <= candle_range / 3 and max(current['open'], current['close']) < (
                current['high'] + current['low']) / 2 and current['high'] > prev['high']:
            self.bearish_pinbar.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_bullish_pinbar(self, candle_range, current, prev, realbody, ticker):
        if realbody <= candle_range / 3 and min(current['open'], current['close']) > (
                current['high'] + current['low']) / 2 and current['low'] < prev['low']:
            self.bullish_pinbar.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_bearish_swing(self, current, prev, prev_2, ticker):
        if current['high'] < prev['high'] and prev['high'] > prev_2['high']:
            self.bearish_swing_codes.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_bullish_swing(self, current, prev, prev_2, ticker):
        if current['low'] > prev['low'] and prev['low'] < prev_2['low']:
            self.bullish_swing_codes.append(f'{ticker}:{current.trading_date}')
            self.matched = True

    def is_bearish_engulfing(self, candle_range, current, prev, realbody, ticker):
        if current['high'] > prev['high'] and current['low'] < prev['low'] and realbody >= 0.8 * candle_range and \
                current[
                    'close'] < current['open']:
            self.bearish_eng_codes.append(f'{ticker}:{current.trading_date}')
            return True
        return False

    def is_bullish_engulfing(self, candle_range, current, prev, realbody, ticker):
        if current['high'] > prev['high'] and current['low'] < prev['low'] and realbody >= 0.8 * candle_range and \
                current[
                    'close'] > current['open']:
            self.bullish_eng_codes.append(f'{ticker}:{current.trading_date}')
            self.matched = True
