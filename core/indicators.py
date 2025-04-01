import pandas as pd


class IndicatorUtils:
    @staticmethod
    def calculate_ema(df, period, column_name):
        """Calculate Exponential Moving Average (EMA) for a given period."""
        df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    @staticmethod
    def calculate_sma(df, period, column_name):
        """Calculate Simple Moving Average (SMA) for a given period."""
        df[column_name] = df['close'].rolling(window=period).mean()
        return df

    @staticmethod
    def calculate_rsi(df, period, column_name):
        """Calculate Relative Strength Index (RSI) for a given period."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df[column_name] = 100 - (100 / (1 + rs))
        return df

    @staticmethod
    def calculate_macd(df, fast_period, slow_period, signal_period):
        """Calculate MACD (Moving Average Convergence Divergence)."""
        df['macd_line'] = df['close'].ewm(span=fast_period, adjust=False).mean() - \
            df['close'].ewm(span=slow_period, adjust=False).mean()
        df['macd_signal'] = df['macd_line'].ewm(
            span=signal_period, adjust=False).mean()
        df['macd_histogram'] = df['macd_line'] - df['macd_signal']
        return df
