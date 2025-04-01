class Config:
    ACCOUNT_NUMBER = 52336957
    PASSWORD = "G4SurPf8@"
    SERVER = "Alpari-MT5-Demo"
    SYMBOL = "EURUSD_i"
    LOT_SIZE = 0.01
    TIMEFRAME = "M1"  # MT5 TIMEFRAME_M1
    TP_PIPS = 5      # Take Profit in pips
    SL_PIPS = 5      # Stop Loss in pips
    CHECK_INTERVAL = 30  # Seconds between checks
    SLEEP_AFTER_TRADE = 60  # Seconds to wait after a trade

    # Convert MT5 timeframe string to MT5 constant
    TIMEFRAMES = {
        "M1": 1,  # mt5.TIMEFRAME_M1
        "M5": 5,
        "M15": 15,
        "H1": 16385
    }

    @staticmethod
    def get_timeframe():
        return Config.TIMEFRAMES.get(Config.TIMEFRAME, 1)
