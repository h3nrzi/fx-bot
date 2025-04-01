import MetaTrader5 as mt5
import pandas as pd


class MarketData:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def fetch_rates(self, num_bars=100):
        rates = mt5.copy_rates_from_pos(
            self.symbol, self.timeframe, 0, num_bars)
        if rates is None:
            print(
                f"Failed to fetch data for {self.symbol}: {mt5.last_error()}")
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_tick(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"Failed to get tick data: {mt5.last_error()}")
            return None
        return tick
