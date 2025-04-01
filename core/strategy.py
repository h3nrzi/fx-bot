class TradingStrategy:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def generate_signals(self, data):
        raise NotImplementedError(
            "Subclasses must implement generate_signals.")
