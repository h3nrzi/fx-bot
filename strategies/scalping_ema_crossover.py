from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class ScalpingEMAStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, short_ema_period, long_ema_period, rsi_period, adx_period, adx_threshold):
        super().__init__(symbol, timeframe)
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period
        self.rsi_period = rsi_period
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold

    def calculate_indicators(self, df):
        # Calculate short EMA and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.short_ema_period,
            column_name='short_ema'
        )
        print(f"Short EMA ({self.short_ema_period}):")
        print(df[['short_ema']].tail())

        # Calculate long EMA and add it to the DataFrame
        df = IndicatorUtils.calculate_ema(
            df=df,
            period=self.long_ema_period,
            column_name='long_ema'
        )
        print(f"Long EMA ({self.long_ema_period}):")
        print(df[['long_ema']].tail())

        # Calculate RSI and add it to the DataFrame
        df = IndicatorUtils.calculate_rsi(
            df=df,
            period=self.rsi_period,
            column_name='rsi'
        )
        print(f"RSI ({self.rsi_period}):")
        print(df[['rsi']].tail())

        # Calculate ADX and add it to the DataFrame
        df = IndicatorUtils.calculate_adx(
            df=df,
            period=self.adx_period,
            column_name='adx'
        )
        print(f"ADX ({self.adx_period}):")
        print(df[['adx']].tail())

        # Calculate the gap between short EMA and long EMA
        df['ema_gap'] = df['short_ema'] - df['long_ema']
        print("EMA gap:")
        print(df[['ema_gap']].tail())

        return df

    def generate_signals(self, df):
        # Calculate all required indicators
        df = self.calculate_indicators(df)

        # Ensure there is enough data to generate signals
        if len(df) < 2:
            print("Not enough data to generate signals.")
            return False, False

        # Get the last two rows of the DataFrame for signal generation
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Buy signal conditions:
        # - Short EMA crosses above Long EMA
        # - RSI is below 70 (not overbought)
        # - EMA gap is widening
        # - ADX is above the threshold (trend strength confirmation)
        buy_signal = (
            last_row['short_ema'] > last_row['long_ema']
            and prev_row['short_ema'] <= prev_row['long_ema']
            and last_row['rsi'] < 70
            and last_row['ema_gap'] > prev_row['ema_gap']
            and last_row['adx'] > self.adx_threshold
        )
        # Debugging messages for buy signal conditions
        if not (last_row['short_ema'] > last_row['long_ema']):
            print("- Short EMA not above Long EMA.")
        if not (prev_row['short_ema'] <= prev_row['long_ema']):
            print("- No crossover detected.")
        if not (last_row['rsi'] < 70):
            print("- RSI overbought (> 70).")
        if not (last_row['ema_gap'] > prev_row['ema_gap']):
            print("- EMA gap not widening.")
        if not (last_row['adx'] > self.adx_threshold):
            print(
                f"- ADX ({last_row['adx']:.2f}) below threshold ({self.adx_threshold}).")

        # Sell signal conditions:
        # - Short EMA crosses below Long EMA
        # - RSI is above 30 (not oversold)
        # - EMA gap is narrowing
        # - ADX is above the threshold (trend strength confirmation)
        sell_signal = (
            last_row['short_ema'] < last_row['long_ema']
            and prev_row['short_ema'] >= prev_row['long_ema']
            and last_row['rsi'] > 30
            and last_row['ema_gap'] < prev_row['ema_gap']
            and last_row['adx'] > self.adx_threshold
        )
        # Debugging messages for sell signal conditions
        if not (last_row['short_ema'] < last_row['long_ema']):
            print("- Short EMA not below Long EMA.")
        if not (prev_row['short_ema'] >= prev_row['long_ema']):
            print("- No crossover detected.")
        if not (last_row['rsi'] > 30):
            print("- RSI oversold (< 30).")
        if not (last_row['ema_gap'] < prev_row['ema_gap']):
            print("- EMA gap not narrowing.")
        if not (last_row['adx'] > self.adx_threshold):
            print(
                f"- ADX ({last_row['adx']:.2f}) below threshold ({self.adx_threshold}).")

        return buy_signal, sell_signal

    def get_name(self):
        # Return the name of the strategy
        return "ScalpingEMAStrategy"
