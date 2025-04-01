import time
from config.config import Config
from core.connection import MT5Connection
from core.data import MarketData
from core.order import OrderManager
from strategies.ema_crossover import EMACrossoverStrategy
import MetaTrader5 as mt5


class TradingBot:
    def __init__(self):
        self.config = Config()

        self.connection = MT5Connection(
            self.config.ACCOUNT_NUMBER,
            self.config.PASSWORD,
            self.config.SERVER
        )

        self.data = MarketData(
            self.config.SYMBOL,
            self.config.get_timeframe()
        )

        self.order_manager = OrderManager(
            self.config.SYMBOL,
            self.config.LOT_SIZE,
            self.config.TP_PIPS,
            self.config.SL_PIPS
        )

        self.strategy = EMACrossoverStrategy(
            self.config.SYMBOL,
            self.config.get_timeframe()
        )

    def run(self):
        if not self.connection.connect() or not self.connection.ensure_symbol(self.config.SYMBOL):
            return

        print("Trading bot started...")
        try:
            while True:
                if mt5.positions_get(symbol=self.config.SYMBOL):
                    print("Position already open. Skipping.")
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                df = self.data.fetch_rates()
                if df is None:
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                buy_signal, sell_signal = self.strategy.generate_signals(df)

                if buy_signal:
                    self.order_manager.place_order('buy')
                    time.sleep(self.config.SLEEP_AFTER_TRADE)
                elif sell_signal:
                    self.order_manager.place_order('sell')
                    time.sleep(self.config.SLEEP_AFTER_TRADE)
                else:
                    print("No signal detected.")
                    time.sleep(self.config.CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("Bot stopped by user.")
        finally:
            self.connection.disconnect()


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
