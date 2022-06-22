# plutus_backtest

[![PyPI](https://img.shields.io/pypi/v/plutus-backtest)](https://pypi.org/project/plutus-backtest/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oanda-backtest)](https://pypi.org/project/plutus-backtest/)
[![Downloads](https://pepy.tech/badge/plutus-backtest)](https://pepy.tech/project/plutus-backtest)

## Description:
This project has been performed for the purpose of local backtests of financial strategies. The package contains various indicators and tools 
allowing users obtaining exact results of their strategies over a certain period of time. The users are also able to pick 
endless amount of trading instruments and set criteria such as long or short positioning. Beside that optional stop loss and take profit
signals are available not only as general limit level for entire portfolio but can be also applied for each instrument individually.
Another optional tool available is weights factor distribution which is oriented to assign weights according to the provided values. 
In addition, the package allows to create full html report containing varius graphs and indicators.

<br />

Tickers for analysis are available on [Yahoo Finance page](https://finance.yahoo.com/).

## Installation: 
* Dependency: **pandas**, **numpy**, **plotly**, **yfinance**, **werkzeug**, **tabulate**
* Install from pypi:
```
pip install plutus_backtest
```
* Verified in Python:

```python
from plutus_backtest import backtest
```
## Examples: 

Class "backtest" contains below parameters:<br />
```
asset: str or list or series
   Instruments taken into the consideration for the backtest.
o_day: list of str or timestamps or series
   Day/Days of the position opening.
c_day: list of str or timestamps or series
   Day/Days of the position closing.
weights_factor: list of int or float or array-like or series default None
   Optional list of factors which will be considered to define the weights for taken companies. By default
   all weights are distributed equally, however if the list of factors provided the backtest will maximize
   the weights towards the one with max weight factor. Negative weight factor will be considered as short selling.
take_profit: list of float or int or series default None
   List of values determining the level till a particular stock shall be traded.
stop_loss: list of float or int or series default None
   List of values determining the level till a particular stock shall be traded.
benchmark: str default None
   A benchmark ticker for comparison with portfolio performance
price_period_relation: str default 'O-C'
   Instruct what part of the trading day a position shall be opened,
   and what part of trading day it shall be closed.
   Possible relations:
   O-C / Open to Close prices
   C-O / Close to Open prices
   C-C / Close to Close prices
   O-O / Open to Open prices
   "Open" - the price at which a security first trades upon the opening of an exchange on a trading day.
   "Close" - value of the last transacted price in a security before the market officially closes.
full_report: bool, optional, default False
   Generates full report as PDF.
major_sample: int or None, optional, default 10
   Based on duration of the trading period as well as weights factor of the asset.
   In order to make understandable visualisation in full report graphs such as weights changes and
   weights distribution, major sample is used which will focus to provide info regarding main provided
   assets. Can be changed to any int. If value is None the backtest will consider all assets as major
   ones.
```

<br />

A short and fast way to run a single backtest would be:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "TWTR", "GC=F"], o_day=["2021-08-01", "2021-08-03", "2021-09-05"],
               c_day=["2021-09-01", "2021-10-04", "2022-03-12"])

```

<br />

As a result you will see a statistical table as well as graphical representation of the portfolio which shows accumulated return.

<br />

![image](https://user-images.githubusercontent.com/83119547/149675789-605bb97c-be06-4297-b7c2-9b821cfdda2a.png)

<br />

In order to access dataframe with portfolio daily changes and weights distribution, use:

<br />

```python
from plutus.backtest import execution

bt, portfolio_daily_changes, portfolio_weights = execution(asset=["AAPL", "TWTR", "GC=F"], o_day=["2021-08-01", "2021-08-03", "2021-09-05"],
               c_day=["2021-09-01", "2021-10-04", "2022-03-12"])


```
<br />

The result will appear as following (all values are in %):

<br />

![image](https://user-images.githubusercontent.com/83119547/149677827-5bf80957-cf17-4d4d-8a57-817cbc976e82.png)

<br />

If you would like to compare performance of your portfolio with any other instrument you can use a parameter "benchmark":

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "TWTR", "FB"], o_day=["2021-08-01", "2021-08-03", "2021-09-05"],
               c_day=["2021-09-01", "2021-10-04", "2022-03-12"], benchmark= ['^GSPC'])

```
<br />

Above example will additionaly plot a S&P 500 index performance (accumulated return from same period as your portfolio) on your portfolio graph:

<br />

![image](https://user-images.githubusercontent.com/83119547/160644004-c2287d34-83b0-480f-87d1-aebe6fd07501.png)

<br />

"Full report" is an optional parameter which allows users users to observe additional graphs frames and indicators:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "F", "MS"], 
              o_day=["2020-08-01", "2020-07-15", "2020-08-20"],
              c_day=["2021-09-01", "2021-09-01", "2021-09-15"], full_report = True)


```
<br />

![Снимок экрана 2022-06-22 095208](https://user-images.githubusercontent.com/83161286/174975152-704667ca-8136-4fcb-90c6-22a04bdd0b32.png)
![Снимок экрана 2022-06-22 095254](https://user-images.githubusercontent.com/83161286/174975164-de073392-bdea-4e55-9b26-32b5f64ebc8c.png)
![Снимок экрана 2022-06-22 095330](https://user-images.githubusercontent.com/83161286/174975169-4487284f-5a16-4a75-b22b-fa5bc0fd4261.png)
![Снимок экрана 2022-06-22 095401](https://user-images.githubusercontent.com/83161286/174975174-db3dacad-7af7-4b9f-b838-562d6d81e0cd.png)

<br />

If the user didn't specified weights of particular assets in your portfolio (using **weights_factor** parameter), % allocation will be distributed equally (in selected period of time) and shown in the last plot called **Weights rebalancing**.

<br />

![1](https://user-images.githubusercontent.com/83161286/174976799-8f858e22-8817-418c-8aa0-4e9cc4eecb0d.png)
![2](https://user-images.githubusercontent.com/83161286/174976837-174a5da5-bfc2-4249-aa9a-9ac0d198bfbb.png)

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "F", "MS"],
              o_day=["2020-08-01", "2020-07-15", "2020-08-20"],
              c_day=["2021-09-01", "2021-09-01", "2021-09-15"],
              weights_factor = [50, 40, 10], full_report = True)

```

<br />

In case of specifying % of portfolio allocation for each asset (AAPL = 50%, F = 40%, MS = 10% from above example) above plots will be adjusted.
Example of Weights distribution plot:

<br />

![3](https://user-images.githubusercontent.com/83161286/174977790-bf5ce252-d0b0-47f5-9b6d-e2e2fc6c48cf.png)
![4](https://user-images.githubusercontent.com/83161286/174977803-e3577a0a-a182-459f-8fe3-416922f66005.png)

<br />

No need to include weights that will sum up to 100% (but it is recommended). Code calculates % based on **value / total of absolute values**. For example:

<br />

```python
from plutus_backtest import backtest

bt = execution(asset=["AAPL", "F", "MS"],
              o_day=["2020-08-01", "2020-07-15", "2020-08-20"],
              c_day=["2021-09-01", "2021-09-01", "2021-09-15"],
              weights_factor = [35, 140, -21], full_report = True)
```

<br />

weights_factor total is 196 [35 + 140 + 21]. <br />
AAPL: 35 / 196 = ~17%<br />
F: 140 / 196 = ~71.4%<br />
MS: |21| / 196 = ~10.7%

Keep in mind that weights factor with "-" sign will indicate short selling for a perticular asset

<br />

![5](https://user-images.githubusercontent.com/83161286/174978869-3876ecf5-59cb-4613-834d-68437283cfcd.png)
![6](https://user-images.githubusercontent.com/83161286/174978875-af5f0758-7f8d-49e0-8402-e6c9757ba5ad.png)

<br />

More complex approach would be assigning weights factor/stop loss/ take profit indicators:

<br />

```python
from plutus.backtest import execution

bt = backtest(asset = ["AAPL", "BTC-USD","GC=F"], 
              o_day = ["2021-08-01", "2021-07-15", "2021-08-20"],
              c_day = ["2021-09-01", "2021-09-01","2021-09-15"], 
              weights_factor = [10, -5, 35], 
              stop_loss = [0.8, 0.9, 0.95], 
              take_profit = [1.1, 1.2, 1.05])

bt.execution()
```

<br />

In this case all parameters are used. The weights will not be distributed equally. "AAPL"  will have 20% of the total portofolio BTC-USD - 10% and 
"GC=F" will have 70%. The negative sign in the weights factor will mean short selling, therefore first "AAPL" and "GC=F" instruments are in long position and 
"BTC-USD" is in the short.

<br />

Stop loss and take profit shall be interpreted as "AAPL" has 20% of stop loss and 10% of take profit, "BTC-USD" has 10% of stop loss and 20% of take profit, "GC=F" 5% of stop loss and 5% of take profit. As result accumulative graph will look as:

<br />

![10](https://user-images.githubusercontent.com/83161286/174981977-e5bcca06-706f-40c1-8d20-71557e94481a.png)
![11](https://user-images.githubusercontent.com/83161286/174981983-c085db26-719d-4f20-aa41-555d26fcd240.png)

<br />

In the moment when one of the securities reaching its stop loss or take profit, the trade will automatically stopped and the weights will be reassigned respectively to the left assets.

<br />

In case of users need to test one instrument but several times with different timelines, the package will interpret it as:

<br />

```python
from plutus.backtest import execution

bt, portfolio_daily_changes = execution(asset = ["AMZN", "AMZN","AMZN"], 
              o_day = ["2021-08-01", "2021-09-01", "2021-10-01"],
              c_day = ["2021-08-15", "2021-09-15","2021-10-15"])

portfolio_daily_changes.head(15)
```

<br />

![image](https://user-images.githubusercontent.com/83119547/149677380-0bfa8600-ce68-4087-9cd7-c114f48490ba.png)

<br />

Each time when one asset is repeating the backtest will assign additional number to it to track required periods. 
It's worth to mention that due to data limitation the code will use only close price for the analysis of the securities. Only the first trading day has relationship open/close, since it's assumed that the tradingstarts with open price and finishes with close one.

<br />



## Support:
Please [open an issue](https://github.com/witmul/backt/issues/new) for support.<br />
With additional questions please reachout to autors directly:
- [witmul](mailto:witalijmulawa@gmail.com)
- [IlliaBoloto](mailto:ils.boloto96@gmail.com)

