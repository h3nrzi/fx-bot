import MetaTrader5 as mt5
import pandas as pd
import sys

# Account details
account_number = 52336957
password = "G4SurPf8@"
server = "Alpari-MT5-Demo"
symbol = "EURUSD_i"

# Connect to MetaTrader 5
if not mt5.initialize(login=account_number, password=password, server=server):
    print("Failed to connect to MetaTrader 5. Please check login credentials.")
    sys.exit()

# Check connection status
terminal_info = mt5.terminal_info()
if terminal_info:
    print("Connection established:")
    print(f"Terminal name: {terminal_info.name}")
    print(f"Version: {terminal_info.build}")
    print(f"Connection status: {terminal_info.connected}")
else:
    print("Terminal info not available.")
    quit()

# Account information
account_info = mt5.account_info()
if account_info:
    print("\nAccount information:")
    print(f"Account number: {account_info.login}")
    print(f"Balance: {account_info.balance} {account_info.currency}")
    print(f"Equity: {account_info.equity}")
    print(f"Free margin: {account_info.margin_free}")
    print(f"Trading allowed: {account_info.trade_allowed}")
else:
    print("Failed to retrieve account information.")

# Symbol information
symbol_info = mt5.symbol_info(symbol)
if symbol_info:
    print("\nSymbol information:")
    print(f"Symbol: {symbol_info.name}")
    print(f"Minimum volume: {symbol_info.volume_min}")
    print(f"Maximum volume: {symbol_info.volume_max}")
    print(f"Tick size: {symbol_info.trade_tick_size}")
    print(f"Point: {symbol_info.point}")
    print(f"Stops level: {symbol_info.stops_level} points")
    print(f"Spread: {symbol_info.spread} points")
    print(f"Profit currency: {symbol_info.currency_profit}")
else:
    print(f"Symbol {symbol} not found.")

# Current tick data
tick = mt5.symbol_info_tick(symbol)
if tick:
    print("\nCurrent tick data:")
    print(f"Ask price: {tick.ask}")
    print(f"Bid price: {tick.bid}")
else:
    print("Failed to retrieve tick data.")

# Disconnect
mt5.shutdown()
print("\nConnection closed.")
