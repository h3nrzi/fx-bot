from core.strategy import TradingStrategy
from core.indicators import IndicatorUtils


class RSIADXStrategy(TradingStrategy):
    def __init__(self, symbol, timeframe, rsi_period, adx_period, rsi_overbought, rsi_oversold, adx_threshold):
        super().__init__(symbol, timeframe)
        self.rsi_period = rsi_period
        self.adx_period = adx_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        self.adx_threshold = adx_threshold

    def calculate_indicators(self, df):
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
        # - RSI is below the oversold threshold
        # - ADX is above the threshold (trend strength confirmation)
        buy_signal = (
            last_row['rsi'] < self.rsi_oversold
            and last_row['adx'] > self.adx_threshold
        )
        if not buy_signal:
            print("No buy signal conditions met.")

        # Sell signal conditions:
        # - RSI is above the overbought threshold
        # - ADX is above the threshold (trend strength confirmation)
        sell_signal = (
            last_row['rsi'] > self.rsi_overbought
            and last_row['adx'] > self.adx_threshold
        )
        if not sell_signal:
            print("No sell signal conditions met.")

        return buy_signal, sell_signal

    def get_name(self):
        # Return the name of the strategy
        return "RSIADXStrategy"
