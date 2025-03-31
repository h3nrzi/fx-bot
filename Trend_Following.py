import MetaTrader5 as mt5
import time
import pandas as pd


class ScalperBot:
    def __init__(self, account_number, password, server, symbol, lot_size, tp_in_numbers, sl_in_numbers, check_interval, sleep_after_trade, timeframe):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.symbol = symbol
        self.lot_size = lot_size
        self.check_interval = check_interval
        self.sleep_after_trade = sleep_after_trade
        self.timeframe = timeframe
        self.tp_in_numbers = tp_in_numbers
        self.sl_in_numbers = sl_in_numbers

        if not mt5.initialize(login=self.account_number, password=self.password, server=self.server):
            raise Exception("Failed to connect to MetaTrader 5")

        account_info = mt5.account_info()
        if account_info is None:
            raise Exception(
                "Unable to fetch account info. Check login credentials.")
        print(f"Connected to account: {account_info.login}")

    def fetch_data(self, num_bars=100):
        rates = mt5.copy_rates_from_pos(
            self.symbol, self.timeframe, 0, num_bars)
        if rates is None:
            raise Exception(
                f"Failed to fetch data for {self.symbol}: {mt5.last_error()}")
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def calculate_indicators(self, df):
        # Calculate short-term and long-term EMAs
        short_ema_period = 5  # Short-term EMA period
        long_ema_period = 7  # Long-term EMA period

        df['short_ema'] = df['close'].ewm(
            span=short_ema_period, adjust=False).mean()
        df['long_ema'] = df['close'].ewm(
            span=long_ema_period, adjust=False).mean()
        df['ema_gap'] = df['short_ema'] - df['long_ema']  # Calculate EMA gap
        return df

    def detect_signal(self, df):
        # Logic for signal detection using EMA relationships
        last_row = df.iloc[-1]
        previous_row = df.iloc[-2]

        # Detect upward trend (bullish signal)
        if (last_row['short_ema'] > last_row['long_ema'] and
            previous_row['short_ema'] <= previous_row['long_ema'] and
                last_row['ema_gap'] > previous_row['ema_gap']):
            buy_signal = True
        else:
            buy_signal = False

        # Detect downward trend (bearish signal)
        if (last_row['short_ema'] < last_row['long_ema'] and
            previous_row['short_ema'] >= previous_row['long_ema'] and
                last_row['ema_gap'] < previous_row['ema_gap']):
            sell_signal = True
        else:
            sell_signal = False

        # Return buy and sell signals
        return buy_signal, sell_signal

    def place_order(self, action):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} not found.")
            return None

        price = mt5.symbol_info_tick(
            self.symbol).ask if action == 'buy' else mt5.symbol_info_tick(self.symbol).bid
        order_type = mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": order_type,
            "price": price,
            "deviation": 10,
            "magic": 234000,
            "comment": f"NewStrategy {action.capitalize()}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(
                f"{action.capitalize()} order placed successfully: Ticket #{result.order}")
            return result.order
        else:
            print(
                f"Failed to place {action} order. Retcode: {result.retcode}" if result else "Order send failed.")
            return None

    def monitor_position(self):
        print("Monitoring open position...")
        while True:
            positions = mt5.positions_get(symbol=self.symbol)
            if not positions:
                print("No open position found. Exiting monitoring.")
                return

            position = positions[0]
            profit = position.profit
            ticket = position.ticket
            position_type = position.type  # 0 for BUY, 1 for SELL
            print(f"Current Profit: {profit}")

            if profit >= self.tp_in_numbers or profit <= -self.sl_in_numbers:
                print(
                    f"Closing position due to profit/loss threshold: {profit}")
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": ticket,
                    "symbol": self.symbol,
                    "volume": position.volume,
                    "type": mt5.ORDER_TYPE_SELL if position_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(self.symbol).bid if position_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(self.symbol).ask,
                    "deviation": 10,
                    "magic": 234000,
                    "comment": "Threshold Close",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_FOC
                }
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"Position closed successfully: Ticket #{ticket}")
                    time.sleep(self.sleep_after_trade)
                    return
                else:
                    print(
                        f"Failed to close position. Retcode: {result.retcode}" if result else "Order send failed.")
            time.sleep(5)

    def run(self):
        print("Starting Scalper bot with placeholder strategy...")
        while True:
            positions = mt5.positions_get(symbol=self.symbol)
            if positions:
                print("Monitoring existing position...")
                self.monitor_position()
                continue

            df = self.fetch_data()
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
                print("No signal detected. Checking again after interval.")
                time.sleep(self.check_interval)


# Instantiate and run
bot = ScalperBot(
    account_number=52336957,
    password="G4SurPf8@",
    server="Alpari-MT5-Demo",
    symbol="EURUSD_i",
    lot_size=0.1,
    check_interval=5,
    sleep_after_trade=60,
    timeframe=mt5.TIMEFRAME_M1,
    tp_in_numbers=5,
    sl_in_numbers=5
)

bot.run()
