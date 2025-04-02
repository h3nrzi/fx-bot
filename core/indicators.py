import pandas as pd


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
        rs = gain / loss.replace(0, 1)  # جلوگیری از تقسیم بر صفر
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
    def calculate_adx(df, period=14, column_name="adx"):
        """Calculate Average Directional Index (ADX) to measure trend strength."""
        df['high-low'] = df['high'] - df['low']
        df['high-close'] = (df['high'] - df['close'].shift()).abs()
        df['low-close'] = (df['low'] - df['close'].shift()).abs()

        df['tr'] = df[['high-low', 'high-close', 'low-close']].max(axis=1)
        df['tr_smooth'] = df['tr'].rolling(window=period).mean()

        df['plus_dm'] = df['high'].diff()
        df['minus_dm'] = df['low'].diff()

        df['plus_dm'] = df['plus_dm'].where(
            (df['plus_dm'] > df['minus_dm']) & (df['plus_dm'] > 0), 0)
        df['minus_dm'] = df['minus_dm'].where(
            (df['minus_dm'] > df['plus_dm']) & (df['minus_dm'] > 0), 0)

        df['plus_di'] = 100 * \
            (df['plus_dm'].rolling(window=period).mean() / df['tr_smooth']).fillna(0)
        df['minus_di'] = 100 * \
            (df['minus_dm'].rolling(window=period).mean() /
             df['tr_smooth']).fillna(0)

        df[column_name] = 100 * abs(df['plus_di'] - df['minus_di']) / \
            (df['plus_di'] + df['minus_di']).replace(0, 1)

        return df.drop(columns=['high-low', 'high-close', 'low-close', 'tr', 'tr_smooth', 'plus_dm', 'minus_dm', 'plus_di', 'minus_di'])
