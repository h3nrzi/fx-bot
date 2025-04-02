from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class EMACrossoverStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_ema_period, long_ema_period):
        super().__init__(symbol, timeframe)
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period

    def calculate_indicators(self, df):
        # Calculate the short EMA and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.short_ema_period,
            column_name='short_ema'
        )
        print(f"Short EMA calculated for period {self.short_ema_period}:")
        print(df[['short_ema']].tail())

        # Calculate the long EMA and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.long_ema_period,
            column_name='long_ema'
        )
        print(f"Long EMA calculated for period {self.long_ema_period}:")
        print(df[['long_ema']].tail())

        # Calculate the gap between short EMA and long EMA
        df['ema_gap'] = df['short_ema'] - df['long_ema']
        print("EMA gap calculated:")
        print(df[['ema_gap']].tail())

        # Calculate the rolling mean of the EMA gap to identify trends
        df['ema_gap_trend'] = df['ema_gap'].rolling(window=5).mean()
        print("EMA gap trend (rolling mean) calculated:")
        print(df[['ema_gap_trend']].tail())

        return df

    def generate_signals(self, df):
        # Calculate indicators before generating signals
        df = self.calculate_indicators(df)

        # Ensure there are at least two rows to compare
        if len(df) < 2:
            print("Not enough data to generate signals.")
            return False, False

        # Get the last and previous rows of the DataFrame
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Check if the EMA gap trend is positive or negative
        ema_gap_trend_positive = df['ema_gap_trend'].iloc[-1] > 0
        ema_gap_trend_negative = df['ema_gap_trend'].iloc[-1] < 0

        print(f"Last row: {last_row.to_dict()}")
        print(f"Previous row: {prev_row.to_dict()}")
        print(f"EMA gap trend positive: {ema_gap_trend_positive}")
        print(f"EMA gap trend negative: {ema_gap_trend_negative}")

        # Generate a buy signal based on EMA crossover and trend conditions
        buy_signal = (
            last_row['short_ema'] > last_row['long_ema']
            and prev_row['short_ema'] <= prev_row['long_ema']
            and last_row['ema_gap'] > prev_row['ema_gap']
            and ema_gap_trend_positive
        )
        print(f"Buy signal: {buy_signal}")

        # Generate a sell signal based on EMA crossover and trend conditions
        sell_signal = (
            last_row['short_ema'] < last_row['long_ema']
            and prev_row['short_ema'] >= prev_row['long_ema']
            and last_row['ema_gap'] < prev_row['ema_gap']
            and ema_gap_trend_negative
        )
        print(f"Sell signal: {sell_signal}")

        return buy_signal, sell_signal

    def get_name(self):
        return "EMACrossoverStrategy"
