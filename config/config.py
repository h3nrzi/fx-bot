import os


class Config:
    ACCOUNT_NUMBER = int(os.getenv("ACCOUNT_NUMBER"))
    PASSWORD = os.getenv("PASSWORD")
    SERVER = os.getenv("SERVER")
    SYMBOL = "EURUSD_i"
    LOT_SIZE = 0.01
    TIMEFRAME = "M1"
    TP_PIPS = 5
    SL_PIPS = 5
    CHECK_INTERVAL = 30
    SLEEP_AFTER_TRADE = 60

    # Convert MT5 timeframe string to MT5 constant
    TIMEFRAMES = {
        "M1": 1,
        "M5": 5,
        "M15": 15,
        "H1": 16385
    }

    @staticmethod
    def get_timeframe():
        return Config.TIMEFRAMES.get(Config.TIMEFRAME)
