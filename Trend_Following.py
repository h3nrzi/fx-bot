import MetaTrader5 as mt5
import time
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class ScalperBot:
    def __init__(self, account_number, password, server, symbol, lot_size, tp_pips, sl_pips, check_interval, sleep_after_trade, timeframe, magic=234000):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.symbol = symbol
        self.lot_size = lot_size
        self.check_interval = check_interval
        self.sleep_after_trade = sleep_after_trade
        self.timeframe = timeframe
        self.tp_pips = tp_pips
        self.sl_pips = sl_pips
        self.magic = magic

        if not mt5.initialize(login=self.account_number, password=self.password, server=self.server):
            raise Exception("Failed to connect to MetaTrader 5")

        account_info = mt5.account_info()
        if account_info is None:
            raise Exception(
                "Unable to fetch account info. Check login credentials.")

        logger.info(f"Connected to account: {account_info.login}")

    def fetch_data(self, num_bars=100):
        rates = mt5.copy_rates_from_pos(
            self.symbol,
            self.timeframe,
            0,
            num_bars
        )

        if rates is None or len(rates) < 3:
            logger.error(
                f"Failed to fetch data for {self.symbol}: {mt5.last_error()}"
            )
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def calculate_indicators(self, df):
        df['short_ema'] = df['close'].ewm(span=10, adjust=False).mean()
        df['long_ema'] = df['close'].ewm(span=50, adjust=False).mean()
        return df

    def detect_signal(self, df):
        if df is None or len(df) < 3:
            logger.warning("Insufficient data for signal detection.")
            return False, False

        last_row = df.iloc[-1]
        previous_row = df.iloc[-2]
        second_last_row = df.iloc[-3]

        short_ema = last_row['short_ema']
        long_ema = last_row['long_ema']
        prev_short_ema = previous_row['short_ema']
        prev_long_ema = previous_row['long_ema']
        second_short_ema = second_last_row['short_ema']
        second_long_ema = second_last_row['long_ema']

        buy_signal = (prev_short_ema <= prev_long_ema and short_ema > long_ema and
                      (short_ema - long_ema) > (prev_short_ema - prev_long_ema) and
                      (prev_short_ema - prev_long_ema) > (second_short_ema - second_long_ema))

        sell_signal = (prev_short_ema >= prev_long_ema and short_ema < long_ema and
                       (long_ema - short_ema) > (prev_long_ema - prev_short_ema) and
                       (prev_long_ema - prev_short_ema) > (second_long_ema - second_short_ema))

        return buy_signal, sell_signal

    def place_order(self, action):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            logger.error(f"Symbol {self.symbol} not found.")
            return None

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            logger.error(
                f"Failed to get tick data for {self.symbol}: {mt5.last_error()}")
            return None

        price = tick.ask if action == 'buy' else tick.bid
        point = symbol_info.point
        tp_price = price + self.tp_pips * \
            point if action == 'buy' else price - self.tp_pips * point
        sl_price = price - self.sl_pips * \
            point if action == 'buy' else price + self.sl_pips * point

        order_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "sl": sl_price,  # Set SL as price level
            "tp": tp_price,  # Set TP as price level
            "deviation": 10,
            "magic": self.magic,
            "comment": f"NewStrategy {action.capitalize()}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(
                f"{action.capitalize()} order placed successfully: Ticket #{result.order}")
            return result.order
        else:
            logger.error(
                f"Failed to place {action} order. Retcode: {result.retcode if result else 'Unknown'}")
            return None

    def monitor_position(self):
        logger.info("Monitoring open position...")
        timeout = time.time() + 3600  # 1-hour timeout to prevent infinite loop
        while time.time() < timeout:
            positions = mt5.positions_get(symbol=self.symbol)
            if not positions:
                logger.info("No open position found. Exiting monitoring.")
                return

            position = positions[0]
            profit = position.profit
            ticket = position.ticket
            logger.info(f"Current Profit for Ticket #{ticket}: {profit}")

            # TP/SL handled by MT5 server-side, so just monitor if position is still open
            time.sleep(5)

        logger.warning("Monitoring timed out after 1 hour.")

    def run(self):
        logger.info("Starting Scalper bot with EMA crossover strategy...")
        while True:
            positions = mt5.positions_get(symbol=self.symbol)
            if positions:
                logger.info("Monitoring existing position...")
                self.monitor_position()
                continue

            df = self.fetch_data()
            if df is None:
                time.sleep(self.check_interval)
                continue

            df = self.calculate_indicators(df)
            buy_signal, sell_signal = self.detect_signal(df)

            if buy_signal:
                ticket = self.place_order('buy')
                if ticket:
                    self.monitor_position()
            elif sell_signal:
                ticket = self.place_order('sell')
                if ticket:
                    self.monitor_position()
            else:
                logger.info(
                    "No signal detected. Checking again after interval.")
                time.sleep(self.check_interval)


# Create and run the bot
bot = ScalperBot(
    account_number=52336957,
    password="G4SurPf8@",
    server="Alpari-MT5-Demo",
    symbol="EURUSD_i",
    lot_size=0.01,
    tp_pips=10,  # 1 pips for EURUSD = 10 points
    sl_pips=10,
    check_interval=30,
    sleep_after_trade=60,
    timeframe=mt5.TIMEFRAME_M1,
    magic=234000
)

bot.run()
