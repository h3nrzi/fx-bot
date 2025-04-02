from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class MovingAverageStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_window, long_window):
        super().__init__(symbol, timeframe)
        self.short_window = short_window
        self.long_window = long_window

    def calculate_indicators(self, df):
        # Calculate short-term moving average and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.short_window,
            column_name='short_ma'
        )
        print(f"Short MA ({self.short_window}):")
        print(df[['short_ma']].tail())

        # Calculate long-term moving average and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.long_window,
            column_name='long_ma'
        )
        print(f"Long MA ({self.long_window}):")
        print(df[['long_ma']].tail())

        return df

    def generate_signals(self, df):
        # Calculate all required indicators
        df = self.calculate_indicators(df)

        # Ensure there is enough data to generate signals
        if len(df) < 1:
            print("Not enough data to generate signals.")
            return False, False

        # Get the last row of the DataFrame for signal generation
        last_row = df.iloc[-1]

        # Buy signal conditions:
        # - Short-term MA crosses above long-term MA
        buy_signal = last_row['short_ma'] > last_row['long_ma']
        if not buy_signal:
            print("No buy signal conditions met.")

        # Sell signal conditions:
        # - Short-term MA crosses below long-term MA
        sell_signal = last_row['short_ma'] < last_row['long_ma']
        if not sell_signal:
            print("No sell signal conditions met.")

        return buy_signal, sell_signal

    def get_name(self):
        # Return the name of the strategy
        return "MovingAverageStrategy"
