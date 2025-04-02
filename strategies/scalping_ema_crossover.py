from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class ScalpingEMAStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_ema_period, long_ema_period, rsi_period):
        super().__init__(symbol, timeframe)
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period
        self.rsi_period = rsi_period

    def calculate_indicators(self, df):
        # Calculate short EMA
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.short_ema_period,
            column_name='short_ema'
        )
        print(f"Short EMA ({self.short_ema_period}):")
        print(df[['short_ema']].tail())

        # Calculate long EMA
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.long_ema_period,
            column_name='long_ema'
        )
        print(f"Long EMA ({self.long_ema_period}):")
        print(df[['long_ema']].tail())

        # Calculate RSI
        df = IndicatorUtils.calculate_rsi(
            df=df,
            period=self.rsi_period,
            column_name='rsi'
        )
        print(f"RSI ({self.rsi_period}):")
        print(df[['rsi']].tail())

        # Calculate EMA gap
        df['ema_gap'] = df['short_ema'] - df['long_ema']
        print("EMA gap:")
        print(df[['ema_gap']].tail())

        return df

    def generate_signals(self, df):
        df = self.calculate_indicators(df)

        if len(df) < 2:
            print("Not enough data to generate signals.")
            return False, False

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Buy signal: Short EMA crosses above Long EMA, RSI < 70, EMA gap widening
        buy_signal = (
            last_row['short_ema'] > last_row['long_ema']
            and prev_row['short_ema'] <= prev_row['long_ema']
            and last_row['rsi'] < 70
            and last_row['ema_gap'] > prev_row['ema_gap']
        )
        if not (last_row['short_ema'] > last_row['long_ema']):
            print("- Short EMA not above Long EMA.")
        if not (prev_row['short_ema'] <= prev_row['long_ema']):
            print("- No crossover detected.")
        if not (last_row['rsi'] < 70):
            print("- RSI overbought (> 70).")
        if not (last_row['ema_gap'] > prev_row['ema_gap']):
            print("- EMA gap not widening.")

        # Sell signal: Short EMA crosses below Long EMA, RSI > 30, EMA gap narrowing
        sell_signal = (
            last_row['short_ema'] < last_row['long_ema']
            and prev_row['short_ema'] >= prev_row['long_ema']
            and last_row['rsi'] > 30
            and last_row['ema_gap'] < prev_row['ema_gap']  # Gap narrowing
        )
        if not (last_row['short_ema'] < last_row['long_ema']):
            print("- Short EMA not below Long EMA.")
        if not (prev_row['short_ema'] >= prev_row['long_ema']):
            print("- No crossover detected.")
        if not (last_row['rsi'] > 30):
            print("- RSI oversold (< 30).")
        if not (last_row['ema_gap'] < prev_row['ema_gap']):
            print("- EMA gap not narrowing.")

        return buy_signal, sell_signal

    def get_name(self):
        return "ScalpingEMAStrategy"
