import MetaTrader5 as mt5
import pandas as pd


class MarketData:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def _handle_fetch_error(self, error_message):
        print(f"{error_message}: {mt5.last_error()}")

    def fetch_rates(self, num_bars=100):
        rates = mt5.copy_rates_from_pos(
            self.symbol, self.timeframe, 0, num_bars)
        if rates is None:
            self._handle_fetch_error(f"Failed to fetch data for {self.symbol}")
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_tick(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            self._handle_fetch_error("Failed to get tick data")
            return None
        return tick

    def get_spread(self):
        """Calculate the spread as the difference between the ask and bid prices."""
        rates = mt5.symbol_info_tick(self.symbol)
        if rates is None:
            print(f"Failed to retrieve tick data for symbol: {self.symbol}")
            return None
        return rates.ask - rates.bid

    def get_current_price(self):
        """Retrieve the current bid and ask prices for the symbol."""
        tick = self.get_tick()
        if tick is None:
            return None
        return {"bid": tick.bid, "ask": tick.ask}
