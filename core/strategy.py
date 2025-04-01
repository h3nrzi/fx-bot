class TradingStrategy:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def calculate_indicators(self, df):
        """Calculate indicators for the strategy. To be overridden by subclasses."""
        raise NotImplementedError(
            "Subclasses must implement calculate_indicators.")

    def generate_signals(self, data):
        """Generate trading signals based on the provided data."""
        raise NotImplementedError(
            "Subclasses must implement generate_signals.")

    def get_name(self):
        """Return the name of the strategy."""
        return self.__class__.__name__
