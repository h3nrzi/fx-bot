from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class ScalpingEMAStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_ema_period=10, long_ema_period=50, rsi_period=14, adx_period=14, adx_threshold=20):
        super().__init__(symbol, timeframe)
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period
        self.rsi_period = rsi_period
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold

    def calculate_indicators(self, df):
        # Short EMA
        df = IndicatorUtils.calculate_ema(
            df, self.short_ema_period, 'short_ema')
        print(f"Short EMA ({self.short_ema_period}):")
        print(df[['short_ema']].tail())

        # Long EMA
        df = IndicatorUtils.calculate_ema(df, self.long_ema_period, 'long_ema')
        print(f"Long EMA ({self.long_ema_period}):")
        print(df[['long_ema']].tail())

        # RSI
        df = IndicatorUtils.calculate_rsi(df, self.rsi_period, 'rsi')
        print(f"RSI ({self.rsi_period}):")
        print(df[['rsi']].tail())

        # ADX (optional confirmation)
        df = IndicatorUtils.calculate_adx(df, self.adx_period, 'adx')
        print(f"ADX ({self.adx_period}):")
        print(df[['adx']].tail())

        return df

    def generate_signals(self, df):
        df = self.calculate_indicators(df)

        if len(df) < 2:
            print("Not enough data to generate signals.")
            return False, False

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Buy signal:
        # - Short EMA crosses above Long EMA
        # - RSI > 20 (not extremely oversold)
        # - ADX optional (if > threshold, stronger signal)
        buy_signal = (
            last_row['short_ema'] > last_row['long_ema']
            and prev_row['short_ema'] <= prev_row['long_ema']
            and last_row['rsi'] > 20
        )
        if buy_signal and last_row['adx'] > self.adx_threshold:
            print("Buy signal strengthened by ADX.")
        elif buy_signal:
            print("Buy signal generated (ADX below threshold, but still valid).")
        else:
            if not (last_row['short_ema'] > last_row['long_ema']):
                print("- Short EMA not above Long EMA.")
            if not (prev_row['short_ema'] <= prev_row['long_ema']):
                print("- No crossover detected.")
            if not (last_row['rsi'] > 20):
                print("- RSI too low (< 20).")

        # Sell signal:
        # - Short EMA crosses below Long EMA
        # - RSI < 80 (not extremely overbought)
        # - ADX optional (if > threshold, stronger signal)
        sell_signal = (
            last_row['short_ema'] < last_row['long_ema']
            and prev_row['short_ema'] >= prev_row['long_ema']
            and last_row['rsi'] < 80
        )
        if sell_signal and last_row['adx'] > self.adx_threshold:
            print("Sell signal strengthened by ADX.")
        elif sell_signal:
            print("Sell signal generated (ADX below threshold, but still valid).")
        else:
            if not (last_row['short_ema'] < last_row['long_ema']):
                print("- Short EMA not below Long EMA.")
            if not (prev_row['short_ema'] >= prev_row['long_ema']):
                print("- No crossover detected.")
            if not (last_row['rsi'] < 80):
                print("- RSI too high (> 80).")

        return buy_signal, sell_signal

    def get_name(self):
        return "ImprovedScalpingEMAStrategy"
