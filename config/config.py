from dotenv import load_dotenv
import os


class Config:
    load_dotenv()
    ACCOUNT_NUMBER = int(os.getenv("ACCOUNT_NUMBER"))
    PASSWORD = os.getenv("PASSWORD")
    SERVER = os.getenv("SERVER")
    SYMBOL = "EURUSD_i"
    LOT_SIZE = 0.01
    TIMEFRAME = "M15"
    TP_PIPS = 30
    SL_PIPS = 10
    CHECK_INTERVAL = 15
    SLEEP_AFTER_TRADE = 15

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
