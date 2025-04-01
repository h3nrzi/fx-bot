import MetaTrader5 as mt5


class MT5Connection:
    def __init__(self, account_number, password, server):
        self.account_number = account_number
        self.password = password
        self.server = server
        self.connected = False

    def _initialize_connection(self):
        return mt5.initialize(
            login=self.account_number,
            password=self.password,
            server=self.server
        )

    def connect(self):
        if not self._initialize_connection():
            print("Failed to connect to MT5.")
            return False
        self.connected = True
        print(f"Connected to account: {mt5.account_info().login}")
        return True

    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print("MT5 connection closed.")

    def is_connected(self):
        return self.connected and mt5.terminal_info() is not None

    def ensure_symbol(self, symbol):
        if not mt5.symbol_select(symbol, True):
            print(f"Symbol {symbol} not available.")
            return False
        return True
