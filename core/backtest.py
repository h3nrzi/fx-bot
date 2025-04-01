import MetaTrader5 as mt5
import pandas as pd


class Backtester:
    def __init__(self, strategy, symbol, timeframe, lot_size, tp_pips, sl_pips, start_date, end_date):
        self.strategy = strategy
        self.symbol = symbol
        self.timeframe = timeframe
        self.lot_size = lot_size
        self.tp_pips = tp_pips
        self.sl_pips = sl_pips
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.trades = []
        self.equity = 1000  # Starting balance in USD (adjustable)

    def fetch_historical_data(self):
        """Fetch historical data from MT5 for the given period."""
        rates = mt5.copy_rates_range(
            self.symbol, self.timeframe, self.start_date, self.end_date)
        if rates is None or len(rates) == 0:
            print(f"Failed to fetch historical data: {mt5.last_error()}")
            return None
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def simulate_trade(self, entry_price, action, entry_time):
        """Simulate a trade with TP and SL in pips."""
        point = mt5.symbol_info(self.symbol).point
        pip_value = 10 * point  # 1 pip = 0.0001 for EURUSD
        tp_distance = self.tp_pips * pip_value
        sl_distance = self.sl_pips * pip_value

        if action == 'buy':
            tp_price = entry_price + tp_distance
            sl_price = entry_price - sl_distance
        else:  # sell
            tp_price = entry_price - tp_distance
            sl_price = entry_price + sl_distance

        return {
            'entry_price': entry_price,
            'tp_price': tp_price,
            'sl_price': sl_price,
            'action': action,
            'entry_time': entry_time,
            'exit_price': None,
            'exit_time': None,
            'profit': 0
        }

    def run(self):
        """Run the backtest simulation."""
        df = self.fetch_historical_data()
        if df is None:
            return

        current_position = None
        pip_value_per_lot = 0.1  # For EURUSD, 0.01 lots: 1 pip = 0.1 USD

        for i in range(1, len(df)):
            data_slice = df.iloc[:i+1]
            buy_signal, sell_signal = self.strategy.generate_signals(
                data_slice)

            # Close existing position if TP or SL hit
            if current_position:
                row = df.iloc[i]
                high = row['high']
                low = row['low']
                if (current_position['action'] == 'buy' and (high >= current_position['tp_price'] or low <= current_position['sl_price'])) or \
                   (current_position['action'] == 'sell' and (low <= current_position['tp_price'] or high >= current_position['sl_price'])):
                    exit_price = current_position['tp_price'] if high >= current_position[
                        'tp_price'] or low <= current_position['tp_price'] else current_position['sl_price']
                    profit_pips = (exit_price - current_position['entry_price']) / (10 * mt5.symbol_info(self.symbol).point) if current_position['action'] == 'buy' else \
                                  (current_position['entry_price'] - exit_price) / \
                        (10 * mt5.symbol_info(self.symbol).point)
                    profit = profit_pips * pip_value_per_lot * self.lot_size * 100  # Convert to USD
                    current_position['exit_price'] = exit_price
                    current_position['exit_time'] = row['time']
                    current_position['profit'] = profit
                    self.trades.append(current_position)
                    self.equity += profit
                    current_position = None

            # Open new position
            if not current_position:
                if buy_signal:
                    current_position = self.simulate_trade(
                        df.iloc[i]['close'], 'buy', df.iloc[i]['time'])
                elif sell_signal:
                    current_position = self.simulate_trade(
                        df.iloc[i]['close'], 'sell', df.iloc[i]['time'])

        self.calculate_performance()

    def calculate_performance(self):
        """Calculate and print backtest performance metrics."""
        if not self.trades:
            print("No trades executed during backtest.")
            return

        total_profit = sum(trade['profit'] for trade in self.trades)
        wins = len([t for t in self.trades if t['profit'] > 0])
        losses = len([t for t in self.trades if t['profit'] <= 0])
        win_rate = wins / len(self.trades) * 100 if self.trades else 0

        print("\nBacktest Results:")
        print(f"Total Trades: {len(self.trades)}")
        print(f"Total Profit: {total_profit:.2f} USD")
        print(f"Final Equity: {self.equity:.2f} USD")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Wins: {wins}, Losses: {losses}")

        # Print trade log (optional)
        for trade in self.trades:
            print(f"Trade: {trade['action']} | Entry: {trade['entry_price']} @ {trade['entry_time']} | "
                  f"Exit: {trade['exit_price']} @ {trade['exit_time']} | Profit: {trade['profit']:.2f} USD")
