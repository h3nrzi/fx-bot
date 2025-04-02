import time
from config.config import Config
from core.connection import MT5Connection
from core.data import MarketData
from core.order import OrderManager
import MetaTrader5 as mt5
from strategies.scalping_ema_crossover import ScalpingEMAStrategy


class TradingBot:
    def __init__(self, strategy, config):
        self.config = config
        self.strategy = strategy
        self._initialize_connection()
        self._initialize_market_data()
        self._initialize_order_manager()
        self.no_signal_counter = 1

    def _initialize_connection(self):
        self.connection = MT5Connection(
            self.config.ACCOUNT_NUMBER,
            self.config.PASSWORD,
            self.config.SERVER
        )

    def _initialize_market_data(self):
        self.data = MarketData(
            self.config.SYMBOL,
            self.config.get_timeframe()
        )

    def _initialize_order_manager(self):
        self.order_manager = OrderManager(
            self.config.SYMBOL,
            self.config.LOT_SIZE,
            self.config.TP_PIPS,
            self.config.SL_PIPS
        )

    def run(self):
        # Ensure connection to the trading platform and symbol availability
        if not self.connection.connect() or not self.connection.ensure_symbol(self.config.SYMBOL):
            return

        print(
            f"Trading bot started using strategy: {self.strategy.get_name()}")

        try:
            while True:
                # Check if there is already an open position for the symbol
                positions = mt5.positions_get(symbol=self.config.SYMBOL)
                if positions:
                    self.no_signal_counter = 1
                    for position in positions:
                        print(
                            f"Position Details:\n"
                            f"  Ticket: {position.ticket}\n"
                            f"  Type: {'Buy' if position.type == 0 else 'Sell'}\n"
                            f"  Volume: {position.volume}\n"
                            f"  Open Price: {position.price_open}\n"
                            f"  Profit: {position.profit}\n"
                            "************************\n"
                        )
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
                    print(
                        f"No signal detected - "
                        f"Market Info: {self.no_signal_counter}\n"
                        f"  Symbol: {self.config.SYMBOL}\n"
                        f"  Timeframe: {self.config.get_timeframe()}\n"
                        f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"  Price: {self.data.get_current_price()}\n"
                        f"  Spread: {self.data.get_spread()}\n"
                        "************************************************************************"
                    )
                    self.no_signal_counter += 1
                    time.sleep(self.config.CHECK_INTERVAL)

        # Handle user interruption gracefully
        except KeyboardInterrupt:
            print("Bot stopped by user.")

        # Disconnect from the trading platform when stopping
        finally:
            self.connection.disconnect()


if __name__ == "__main__":
    config_instance = Config()

    strategy_instance = ScalpingEMAStrategy(
        symbol=Config.SYMBOL,
        timeframe=Config.get_timeframe(),
        short_ema_period=5,
        long_ema_period=13,
        rsi_period=14
    )

    bot = TradingBot(
        config=config_instance,
        strategy=strategy_instance,
    )

    bot.run()
