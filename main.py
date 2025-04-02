def run(self):
    # Notify bot startup
    startup_message = (
        f"🚀 Trading bot started! 📈 Monitoring {self.config.SYMBOL} with lot size {self.config.LOT_SIZE} "
        f"and trading frequency {self.config.CHECK_INTERVAL} seconds."
    )
    print(startup_message)
    self.notifier.send_message(startup_message)

    if not self.connection.connect() or not self.connection.ensure_symbol(self.config.SYMBOL):
        error_message = "❌ Connection failed! Please check your account credentials or symbol settings."
        print(error_message)
        self.notifier.send_message(error_message)
        return

    print(f"🤖 Trading bot started using strategy: {self.strategy.get_name()}")

    try:
        while True:
            positions = mt5.positions_get(symbol=self.config.SYMBOL)
            if positions:
                self.no_signal_counter = 1
                for position in positions:
                    position_message = (
                        f"📊 Position update for {self.config.SYMBOL}: "
                        f"💰 Current profit: {position.profit:.2f}."
                    )
                    print(position_message)
                    self.notifier.send_message(position_message)
                time.sleep(self.config.CHECK_INTERVAL)
                continue

            df = self.data.fetch_rates()
            if df is None:
                time.sleep(self.config.CHECK_INTERVAL)
                continue

            buy_signal, sell_signal = self.strategy.generate_signals(df)

            if buy_signal or sell_signal:
                action = 'buy' if buy_signal else 'sell'
                signal_message = (
                    f"📢 Signal detected for {self.config.SYMBOL}! 📊 Preparing to place a {action.upper()} order."
                )
                print(signal_message)
                self.notifier.send_message(signal_message)

                result = self.order_manager.place_order(action)
                if result:
                    if isinstance(result, int):
                        success_message = (
                            f"✅ Order placed successfully: {action.upper()} {self.config.SYMBOL}. "
                            f"🎟️ Ticket ID: {result}."
                        )
                    else:
                        success_message = (
                            f"✅ Order placed successfully: {action.upper()} {self.config.SYMBOL} at price {result.price:.2f}. "
                            f"🎟️ Ticket ID: {result.order}."
                        )
                    print(success_message)
                    self.notifier.send_message(success_message)
                else:
                    error_message = (
                        f"❌ Order placement failed: {action.upper()} {self.config.SYMBOL}. "
                        f"⚠️ Error code: {mt5.last_error()}."
                    )
                    print(error_message)
                    self.notifier.send_message(error_message)

                time.sleep(self.config.SLEEP_AFTER_TRADE)
            else:
                no_signal_message = (
                    f"🔍 No signal detected - Market Info: {self.no_signal_counter}\n"
                    f"  📌 Symbol: {self.config.SYMBOL}\n"
                    f"  ⏱️ Timeframe: {self.config.get_timeframe()}\n"
                    f"  🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"  💵 Price: {self.data.get_current_price():.2f}\n"
                    f"  📉 Spread: {self.data.get_spread():.2f}\n"
                    "************************************************************************"
                )
                print(no_signal_message)
                self.notifier.send_message(no_signal_message)
                self.no_signal_counter += 1
                time.sleep(self.config.CHECK_INTERVAL)

    except KeyboardInterrupt:
        stop_message = "🛑 Bot stopped by user. Goodbye! 👋"
        print(stop_message)
        self.notifier.send_message(stop_message)

    finally:
        self.connection.disconnect()
