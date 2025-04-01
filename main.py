import time
from config.config import Config
from core.connection import MT5Connection
from core.data import MarketData
from core.order import OrderManager
from core.backtest import Backtester
from strategies.ema_crossover import EMACrossoverStrategy
import MetaTrader5 as mt5


class TradingBot:
    def __init__(self, backtest=False, start_date=None, end_date=None):
        # Load configuration settings
        self.config = Config()

        # Initialize connection to the trading platform
        self.connection = MT5Connection(
            self.config.ACCOUNT_NUMBER,
            self.config.PASSWORD,
            self.config.SERVER)

        # Initialize market data handler
        self.data = MarketData(
            self.config.SYMBOL,
            self.config.get_timeframe())

        # Initialize order manager for placing and managing trades
        self.order_manager = OrderManager(
            self.config.SYMBOL,
            self.config.LOT_SIZE,
            self.config.TP_PIPS,
            self.config.SL_PIPS)

        # Initialize the trading strategy
        self.strategy = EMACrossoverStrategy(
            self.config.SYMBOL,
            self.config.get_timeframe())

        # Set backtesting parameters
        self.backtest = backtest
        self.start_date = start_date
        self.end_date = end_date

    ####################################################################################

    def run_backtest(self):
        # Establish a connection to the trading platform
        if not self.connection.connect():
            return

        # Initialize the backtester with the strategy and configuration parameters
        backtester = Backtester(
            self.strategy,
            self.config.SYMBOL,
            self.config.get_timeframe(),
            self.config.LOT_SIZE,
            self.config.TP_PIPS,
            self.config.SL_PIPS,
            self.start_date,
            self.end_date)

        # Run the backtesting process
        backtester.run()

        # Disconnect from the trading platform after backtesting
        self.connection.disconnect()

    ####################################################################################

    def run_live(self):
        # Ensure connection to the trading platform and symbol availability
        if not self.connection.connect() or not self.connection.ensure_symbol(self.config.SYMBOL):
            return

        print("Trading bot started...")

        try:
            while True:
                # Check if there is already an open position for the symbol
                if mt5.positions_get(symbol=self.config.SYMBOL):
                    print("Position already open. Skipping.")
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                # Fetch the latest market data
                df = self.data.fetch_rates()
                if df is None:
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                # Generate buy and sell signals based on the strategy
                buy_signal, sell_signal = self.strategy.generate_signals(df)

                # Place a buy order if a buy signal is detected
                if buy_signal:
                    self.order_manager.place_order('buy')
                    time.sleep(self.config.SLEEP_AFTER_TRADE)
                # Place a sell order if a sell signal is detected
                elif sell_signal:
                    self.order_manager.place_order('sell')
                    time.sleep(self.config.SLEEP_AFTER_TRADE)
                # If no signal is detected, wait for the next interval
                else:
                    print("No signal detected.")
                    time.sleep(self.config.CHECK_INTERVAL)

        # Handle user interruption gracefully
        except KeyboardInterrupt:
            print("Bot stopped by user.")

        # Disconnect from the trading platform when stopping
        finally:
            self.connection.disconnect()

    ####################################################################################

    def run(self):
        if self.backtest:
            self.run_backtest()
        else:
            self.run_live()


if __name__ == "__main__":
    # Live trading
    # bot = TradingBot()
    # bot.run()

    # Backtesting
    bot = TradingBot(
        backtest=True,
        start_date="2024-01-01",
        end_date="2024-12-01")
    bot.run()
