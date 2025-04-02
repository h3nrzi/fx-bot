import MetaTrader5 as mt5


class OrderManager:
    def __init__(self, symbol, lot_size, tp_pips, sl_pips):
        self.symbol = symbol
        self.lot_size = lot_size
        self.tp_pips = tp_pips
        self.sl_pips = sl_pips

    def _validate_symbol(self):
        # Validate if the symbol exists in the MetaTrader 5 platform
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            print(f"Symbol {self.symbol} not found.")
            return None
        return symbol_info

    def place_order(self, action):
        # Place a buy or sell order based on the specified action ('buy' or 'sell')
        symbol_info = self._validate_symbol()
        if not symbol_info:
            return None

        # Get the latest tick data for the symbol
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            print(f"Failed to get tick data: {mt5.last_error()}")
            return None

        # Determine the price based on the action (ask price for buy, bid price for sell)
        price = tick.ask if action == 'buy' else tick.bid
        point = symbol_info.point  # The smallest price change for the symbol
        pip_value = 10 * point  # 1 pip = 0.0001
        tp_distance = self.tp_pips * pip_value  # Calculate TP distance in price
        sl_distance = self.sl_pips * pip_value  # Calculate SL distance in price
        min_stop_distance = symbol_info.trade_stops_level * \
            point  # Minimum stop level allowed by the broker

        print(f"Price: {price}")
        print(f"Point: {point}")
        print(f"Minimum Stop Distance: {min_stop_distance}")

        # Calculate TP and SL prices based on the action
        if action == 'buy':
            tp_price = price + tp_distance
            sl_price = price - sl_distance
        else:
            tp_price = price - tp_distance
            sl_price = price + sl_distance

        # Ensure TP and SL prices meet the broker's minimum stop level requirements
        if abs(tp_price - price) < min_stop_distance:
            tp_price = price + min_stop_distance if action == 'buy' else price - min_stop_distance
        if abs(sl_price - price) < min_stop_distance:
            sl_price = price - min_stop_distance if action == 'buy' else price + min_stop_distance

        print(f"Calculated TP: {tp_price}, SL: {sl_price}")

        # Check if TP or SL violates the broker's minimum stop level requirements
        if min_stop_distance > 0:
            if abs(price - tp_price) < min_stop_distance or abs(price - sl_price) < min_stop_distance:
                print(
                    "Error: TP or SL does not meet the broker's minimum stop level requirements.")
                return None

        # Create the order request dictionary
        request = {
            # Action type: deal (market order)
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,  # Symbol to trade
            "volume": self.lot_size,  # Lot size
            # Order type (buy or sell)
            "type": mt5.ORDER_TYPE_BUY if action == 'buy' else mt5.ORDER_TYPE_SELL,
            "price": price,  # Execution price
            "sl": sl_price,  # Stop loss price
            "tp": tp_price,  # Take profit price
            "deviation": 50,  # Maximum price deviation allowed (in points)
            "magic": 123456,  # Magic number to identify the order
            "comment": f"{action.capitalize()} Order",  # Order comment
            # Order time type (Good Till Canceled)
            "type_time": mt5.ORDER_TIME_GTC,
            # Order filling type (Fill or Kill)
            "type_filling": mt5.ORDER_FILLING_FOK
        }

        # Send the order request to the MetaTrader 5 platform
        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            # Order placed successfully
            print(f"{action.capitalize()} order placed: Ticket #{result.order}")
            return result.order
        else:
            # Order placement failed
            print(
                f"Order failed. Retcode: {result.retcode if result else 'N/A'}, Error: {mt5.last_error()}")
            return None
