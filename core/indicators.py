import pandas as pd
import numpy as np


class IndicatorUtils:
    @staticmethod
    def calculate_ema(df, period, column_name="ema"):
        """Calculate Exponential Moving Average (EMA) for a given period."""
        df[column_name] = df['close'].ewm(
            span=period, adjust=False).mean().fillna(0)
        return df

    @staticmethod
    def calculate_sma(df, period, column_name="sma"):
        """Calculate Simple Moving Average (SMA) for a given period."""
        df[column_name] = df['close'].rolling(window=period).mean().fillna(0)
        return df

    @staticmethod
    def calculate_rsi(df, period, column_name="rsi"):
        """Calculate Relative Strength Index (RSI) for a given period."""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, 1)
        df[column_name] = 100 - (100 / (1 + rs)).fillna(0)
        return df

    @staticmethod
    def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9, macd_column="macd"):
        """Calculate MACD with customizable column names."""
        df[f'{macd_column}_line'] = df['close'].ewm(span=fast_period, adjust=False).mean() - \
            df['close'].ewm(span=slow_period, adjust=False).mean()
        df[f'{macd_column}_signal'] = df[f'{macd_column}_line'].ewm(
            span=signal_period, adjust=False).mean()
        df[f'{macd_column}_histogram'] = df[f'{macd_column}_line'] - \
            df[f'{macd_column}_signal']
        return df

    @staticmethod
    def calculate_adx(df, period=14, column_name='adx'):
        """Calculate the Average Directional Index (ADX) for a given period."""
        # Calculate True Range (TR)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # Calculate Positive and Negative Directional Movement (DM)
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # Smooth True Range and Directional Movement using Exponential Moving Average
        tr_smooth = tr.ewm(span=period, adjust=False).mean()
        plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
        minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()

        # Calculate Positive and Negative Directional Index (DI)
        plus_di = 100 * (plus_dm_smooth / tr_smooth)
        minus_di = 100 * (minus_dm_smooth / tr_smooth)

        # Calculate Directional Index (DX) and Average Directional Index (ADX)
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        df[column_name] = dx.ewm(span=period, adjust=False).mean()

        return df
