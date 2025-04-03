import time
from config.config import Config
from core.connection import MT5Connection
from core.data import MarketData
from core.order import OrderManager
import MetaTrader5 as mt5
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.scalping_ema_crossover import ScalpingEMAStrategy
from utils.notifications import TelegramNotifier


class TradingBot:
    def __init__(self, strategy, config):
        self.config = config
        self.strategy = strategy
        self.notifier = TelegramNotifier()
        self._initialize_connection()
        self._initialize_market_data()
        self._initialize_order_manager()
        self.no_signal_counter = 1

    def _initialize_connection(self):
        """Initialize the connection to the MetaTrader 5 platform"""
        self.connection = MT5Connection(
            self.config.ACCOUNT_NUMBER,
            self.config.PASSWORD,
            self.config.SERVER
        )

    def _initialize_market_data(self):
        """Initialize the market data object for fetching price data"""
        self.data = MarketData(
            self.config.SYMBOL,
            self.config.get_timeframe()
        )

    def _initialize_order_manager(self):
        """Initialize the order manager for placing and managing trades"""
        self.order_manager = OrderManager(
            self.config.SYMBOL,
            self.config.LOT_SIZE,
            self.config.TP_PIPS,
            self.config.SL_PIPS
        )

    def _format_position_details(self, position):
        """Format detailed position information for notifications"""
        position_type = "⬆️ BUY" if position.type == mt5.ORDER_TYPE_BUY else "⬇️ SELL"
        time_open = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(position.time))

        message = (
            f"📊 Position Update for {self.config.SYMBOL}\n"
            f"🎟️ Ticket: {position.ticket}\n"
            f"📈 Type: {position_type}\n"
            f"📏 Volume: {position.volume:.2f}\n"
            f"💰 Open Price: {position.price_open:.5f}\n"
            f"💵 Current Price: {position.price_current:.5f}\n"
            f"🎯 Take Profit: {position.tp:.5f}\n"
            f"🛑 Stop Loss: {position.sl:.5f}\n"
            f"💲 Profit: {position.profit:.2f}\n"
            f"⏰ Opened: {time_open}\n"
            f"💱 Swap: {position.swap:.2f}"
        )
        return message

    def run(self):
        # Notify bot startup
        startup_message = (
            f"🚀 Trading Bot Started!\n"
            f"📈 Symbol: {self.config.SYMBOL}\n"
            f"📏 Lot Size: {self.config.LOT_SIZE}\n"
            f"⏱️ Check Interval: {self.config.CHECK_INTERVAL}s\n"
            f"🎯 TP: {self.config.TP_PIPS} pips\n"
            f"🛑 SL: {self.config.SL_PIPS} pips"
        )
        print(startup_message)
        self.notifier.send_message(startup_message)

        # Attempt to connect to the trading platform and ensure the symbol is available
        if not self.connection.connect() or not self.connection.ensure_symbol(self.config.SYMBOL):
            error_message = "❌ Connection failed! Please check your account credentials or symbol settings."
            print(error_message)
            self.notifier.send_message(error_message)
            return
        else:
            print(
                f"🤖 Trading bot started using strategy: {self.strategy.get_name()}")

        try:
            while True:
                # Check for open positions
                positions = mt5.positions_get(symbol=self.config.SYMBOL)
                if positions:
                    self.no_signal_counter = 1
                    for position in positions:
                        position_message = self._format_position_details(
                            position=position
                        )
                        print(position_message)
                        self.notifier.send_message(position_message)
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                # Fetch market data
                df = self.data.fetch_rates()
                if df is None:
                    time.sleep(self.config.CHECK_INTERVAL)
                    continue

                # Generate buy/sell signals using the strategy
                buy_signal, sell_signal = self.strategy.generate_signals(df)

                if buy_signal or sell_signal:
                    action = 'buy' if buy_signal else 'sell'
                    signal_message = (
                        f"📢 Signal Detected!\n"
                        f"📈 Symbol: {self.config.SYMBOL}\n"
                        f"📊 Action: {action.upper()}\n"
                        f"💵 Current Price: {self.data.get_current_price()['bid']:.5f}\n"
                        f"⏰ Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    print(signal_message)
                    self.notifier.send_message(signal_message)

                    # Place the order based on the signal
                    result = self.order_manager.place_order(action)
                    if result:
                        if isinstance(result, int):
                            success_message = (
                                f"✅ Order Placed Successfully!\n"
                                f"📈 {action.upper()} {self.config.SYMBOL}\n"
                                f"🎟️ Ticket ID: {result}"
                            )
                        else:
                            success_message = (
                                f"✅ Order Placed Successfully!\n"
                                f"📈 {action.upper()} {self.config.SYMBOL}\n"
                                f"💵 Price: {result.price:.5f}\n"
                                f"🎟️ Ticket ID: {result.order}"
                            )
                        print(success_message)
                        self.notifier.send_message(success_message)
                    else:
                        error_message = (
                            f"❌ Order Placement Failed!\n"
                            f"📈 {action.upper()} {self.config.SYMBOL}\n"
                            f"⚠️ Error: {mt5.last_error()}"
                        )
                        print(error_message)
                        self.notifier.send_message(error_message)

                    time.sleep(self.config.SLEEP_AFTER_TRADE)
                else:
                    # No signal detected, notify and wait
                    no_signal_message = (
                        f"🔍 No Signal Detected #{self.no_signal_counter}\n"
                        f"📌 Symbol: {self.config.SYMBOL}\n"
                        f"⏱️ Timeframe: {self.config.get_timeframe()}\n"
                        f"🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"💵 Price: {self.data.get_current_price()['bid']:.5f}\n"
                        f"📉 Spread: {self.data.get_spread():.5f}\n"
                    )
                    print(no_signal_message)
                    self.notifier.send_message(no_signal_message)
                    self.no_signal_counter += 1
                    time.sleep(self.config.CHECK_INTERVAL)

        # Handle user interruption (Ctrl+C)
        except KeyboardInterrupt:
            stop_message = "🛑 Bot stopped by user. Goodbye! 👋"
            print(stop_message)
            self.notifier.send_message(stop_message)

        # Disconnect from the trading platform
        finally:
            self.connection.disconnect()


if __name__ == "__main__":
    # Load configuration
    config_instance = Config()

    # Initialize the trading strategy
    strategy_instance = ScalpingEMAStrategy(
        symbol=config_instance.SYMBOL,
        timeframe=config_instance.get_timeframe(),
        short_ema_period=5,
        long_ema_period=13,
        rsi_period=7,
        adx_period=14,
        adx_threshold=25
    )

    # Create and run the trading bot
    bot = TradingBot(
        config=config_instance,
        strategy=strategy_instance,
    )

    bot.run()
