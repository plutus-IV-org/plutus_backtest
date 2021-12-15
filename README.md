This library was created for the purpose of local tests of financial strategies. The library contains various indicators and tools 
allowing users obtaining exact results of their strategies over a certain period of time. The users are also able to pick 
endless amount of trading instruments and set criteria such as long or short positioning. Beside that optional stop loss and take profit
signals are available not only as general limit level for entire portfolio but can be also applied for each instrument individually.
Another optional tool available is weights factor distribution which is oriented to assign weights according to the provided values. 
In addition, the library allows to create several backtests and combine them all together into one to see the full picture of the investment 
strategy.

Starting with
pip install ...

A short and fast way to run a single backtest would be:
bt = backtest(... = ["AAPL", "GC-F","BTC-USD"], o_day = ["2021-08-01", "2021-06-15", "2021-09-01"],c_day =  ["2021-09-01", "2021-09-01","2021-09-15"])
bt.run()

The final outcome will provide you general statistic as well as graphical representation of the portfolio change together with
drawdown and monthly income plots.

More complex approach would be assigning weights factor/stop loss/ take profit indicators:
bt = backtest(... = ["AAPL", "GC-F","BTC-USD"], o_day = ["2021-08-01", "2021-06-15", "2021-09-01"],c_day =  ["2021-09-01", "2021-09-01","2021-09-15"],
weights_factor = [10, 20, -20], take_profit = [1.2,1.1,1.05], stop_loss = [0.9, 0.8, 0.95])
bt.run()

In this case the wights will not distributed equally. "AAPL"  will have 20% of the total portoflio GC-F - 40% and 
"BTC-USD" will have 40%. The negative sign in the weights factor will mean short selling, therefore first 2 instruments are in long and 
the last is in the short.


