from abc import ABC, abstractmethod


class TradingStrategy(ABC):
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    @abstractmethod
    def calculate_indicators(self, df):
        """Calculate indicators for the strategy. To be overridden by subclasses."""
        pass

    @abstractmethod
    def generate_signals(self, data):
        """Generate trading signals based on the provided data."""
        pass

    def get_name(self):
        """Return the name of the strategy."""
        return self.__class__.__name__
