import MetaTrader5 as mt5
import sys

# Account details
account_number = 52336957
password = "G4SurPf8@"
server = "Alpari-MT5-Demo"
symbol = "EURUSD_i"
lot_size = 0.01
tp_in_pips = 5
sl_in_pips = 5

# Connect to MetaTrader 5
if not mt5.initialize(login=account_number, password=password, server=server):
    print("Failed to connect to MetaTrader 5. Check credentials or server.")
    sys.exit()

# Ensure symbol is available
if not mt5.symbol_select(symbol, True):
    print(f"Symbol {symbol} not available.")
    mt5.shutdown()
    quit()

# Get symbol info and tick data
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"Symbol {symbol} not found.")
    mt5.shutdown()
    quit()

tick = mt5.symbol_info_tick(symbol)
if tick is None:
    print(f"Failed to get tick data: {mt5.last_error()}")
    mt5.shutdown()
    quit()

# Prepare order (Buy as a test)
price = tick.ask
point = symbol_info.point  # 0.00001
pip_value = 10 * point  # 1 pip = 0.0001 = 10 points for EURUSD
tp_distance = tp_in_pips * pip_value  # e.g., 50 pips = 0.0050
sl_distance = sl_in_pips * pip_value  # e.g., 50 pips = 0.0050
min_stop_distance = 10 * point  # Assume 10 points minimum

tp_price = price + tp_distance
sl_price = price - sl_distance

# Adjust SL/TP if too close
if abs(tp_price - price) < min_stop_distance:
    tp_price = price + min_stop_distance
if abs(sl_price - price) < min_stop_distance:
    sl_price = price - min_stop_distance

print(f"Entry price: {price}")
print(f"TP price: {tp_price} ({(tp_price - price) / pip_value} pips)")
print(f"SL price: {sl_price} ({(price - sl_price) / pip_value} pips)")

request = {
    "action": mt5.TRADE_ACTION_DEAL,
    "symbol": symbol,
    "volume": lot_size,
    "type": mt5.ORDER_TYPE_BUY,
    "price": price,
    "sl": sl_price,
    "tp": tp_price,
    "deviation": 20,
    "magic": 123456,
    "comment": "Test Order",
    "type_time": mt5.ORDER_TIME_GTC,
    "type_filling": mt5.ORDER_FILLING_FOK
}

# Send the order
result = mt5.order_send(request)
if result and result.retcode == mt5.TRADE_RETCODE_DONE:
    print(f"Test Buy order placed successfully: Ticket #{result.order}")
else:
    print(
        f"Order placement failed. Retcode: {result.retcode if result else 'N/A'}, Error: {mt5.last_error()}")

# Disconnect
mt5.shutdown()
print("Connection closed.")
