import MetaTrader5 as mt5


class OrderManager:
    def __init__(self, symbol, lot_size, tp_pips, sl_pips):
        self.symbol = symbol
        self.lot_size = lot_size
        self.tp_pips = tp_pips
        self.sl_pips = sl_pips

    def place_order(self, action):
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} not found.")
            return None

        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"Failed to get tick data: {mt5.last_error()}")
            return None

        price = tick.ask if action == 'buy' else tick.bid
        point = symbol_info.point
        pip_value = 10 * point  # 1 pip = 0.0001
        tp_distance = self.tp_pips * pip_value
        sl_distance = self.sl_pips * pip_value
        min_stop_distance = 10 * point

        if action == 'buy':
            tp_price = price + tp_distance
            sl_price = price - sl_distance
        else:
            tp_price = price - tp_distance
            sl_price = price + sl_distance

        if abs(tp_price - price) < min_stop_distance:
            tp_price = price + min_stop_distance if action == 'buy' else price - min_stop_distance
        if abs(sl_price - price) < min_stop_distance:
            sl_price = price - min_stop_distance if action == 'buy' else price + min_stop_distance

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": self.lot_size,
            "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl_price,
            "tp": tp_price,
            "deviation": 20,
            "magic": 234000,
            "comment": f"{action.capitalize()} Order",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"{action.capitalize()} order placed: Ticket #{result.order}")
            return result.order
        else:
            print(
                f"Order failed. Retcode: {result.retcode if result else 'N/A'}, Error: {mt5.last_error()}")
            return None
