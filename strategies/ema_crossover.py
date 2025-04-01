from core.strategy import TradingStrategy
import pandas as pd


class EMACrossoverStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_ema_period=20, long_ema_period=100):
        super().__init__(symbol, timeframe)
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period

    def _calculate_ema(self, df, period, column_name):
        df[column_name] = df['close'].ewm(span=period, adjust=False).mean()

    def calculate_indicators(self, df):
        self._calculate_ema(df, self.short_ema_period, 'short_ema')
        self._calculate_ema(df, self.long_ema_period, 'long_ema')
        df['ema_gap'] = df['short_ema'] - df['long_ema']
        return df

    def generate_signals(self, df):
        df = self.calculate_indicators(df)
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        buy_signal = (last_row['short_ema'] > last_row['long_ema'] and
                      prev_row['short_ema'] <= prev_row['long_ema'] and
                      last_row['ema_gap'] > prev_row['ema_gap'])

        sell_signal = (last_row['short_ema'] < last_row['long_ema'] and
                       prev_row['short_ema'] >= prev_row['long_ema'] and
                       last_row['ema_gap'] < prev_row['ema_gap'])

        return buy_signal, sell_signal

    def get_name(self):
        return "EMACrossoverStrategy"
