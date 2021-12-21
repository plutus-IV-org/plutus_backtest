# Project_name
## Project description

This library was created for the purpose of local tests of financial strategies. The library contains various indicators and tools 
allowing users obtaining exact results of their strategies over a certain period of time. The users are also able to pick 
endless amount of trading instruments and set criteria such as long or short positioning. Beside that optional stop loss and take profit
signals are available not only as general limit level for entire portfolio but can be also applied for each instrument individually.
Another optional tool available is weights factor distribution which is oriented to assign weights according to the provided values. 
In addition, the library allows to create several backtests and combine them all together into one to see the full picture of the investment 
strategy.

## Installation: 
* Dependency: pandas, numpy, plotly, yfinance
* Install from pypi:
```
pip install project_name 
```
* Verified in Python:
```python
from backt.backt import backtest
```
## Examples: 
A short and fast way to run a single backtest would be:

```python
from backt.backt import backtest
bt = backtest(asset = ["AAPL", "BTC-USD","GC=F"], o_day = ["2021-08-01", "2021-07-15", "2021-08-20"],
              c_day = ["2021-09-01", "2021-09-01","2021-09-15"])
bt.execution()
```

As a result you will see a statistical table as well as graphical representation of the portfolio which shows accumulated return.

![1](https://user-images.githubusercontent.com/83161286/146902663-33525a28-d62e-45b1-9561-cbf0ce1b559a.png)

In order to access dataframe with daily changes, use:
```
bt.final_portfolio.head()
```
The result will appear as following:

![2](https://user-images.githubusercontent.com/83161286/146903435-f88144f7-adbb-447d-92ce-a9f5f35723b7.png)

Next example will generate graphical representation of the portfolio change together with
drawdown and monthly income plots:

```python
from backt.backt import backtest
bt = backtest(["NAVI", "BTC-USD"],
              ["2021-09-01", "2021-08-01", ],
              ["2021-10-15", "2021-12-01"])
bt.plotting()
```

More complex approach would be assigning weights factor/stop loss/ take profit indicators:

```python
from backt.backt import backtest
bt = backtest(comp = ["AAPL", "NAVI","BTC-USD"], 
              o_day = ["2021-08-01", "2021-06-15", "2021-09-01"],
              c_day =  ["2021-09-01", "2021-09-01", "2021-09-15"],
              weights_factor = [10, 20, -20], 
              take_profit = [1.2,1.1,1.05], 
              stop_loss = [0.9, 0.8, 0.95])
bt.portfolio_construction()
```

In this case we are using all parameters. The weights will not distributed equally. "AAPL"  will have 20% of the total portoflio NAVI - 40% and 
"BTC-USD" will have 40%. The negative sign in the weights factor will mean short selling, therefore first 2 instruments are in long and 
the last is in the short.


