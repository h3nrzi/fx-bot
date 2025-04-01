class TradingStrategy:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def generate_signals(self, data):
        raise NotImplementedError(
            "Subclasses must implement generate_signals.")

    def get_name(self):
        """Return the name of the strategy."""
        return self.__class__.__name__
