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
* Dependency: **pandas**, **numpy**, **plotly**, **yfinance**, **dash**, **tabulate**
* Install from pypi:
```
pip install plutus_backtest
```
* Verified in Python:

```python
from plutus.backtest import execution
```

## Examples: 

Function "execution" contains below parameters:<br />
```
   asset: str or list or series
       Instruments taken into the consideration for the backtest.
   start: list of str or timestamps or series
       Day/Days of the position opening.
   end: list of str or timestamps or series
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
    only_working_days: bool, default False
        Based on asset specification, the asset may be traded during the weekends or holidays, in order to
        avoid such impact True parameter might be used.
    non_working_days_rebalance: bool, default False
        If there are assets traded on weekends or holidays partial amount of portfolio weights is kept.
        If the parameter is True the weights from non-traded assets will be rebalanced as per active assets
        and its weights_factor.
    broker_commission: float, default 0
        Setting brokerage commission per each trade.
```

<br />

A short and fast way to run a single backtest would be:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "BTC-USD", "GC=F"], start=["2021-08-01", "2021-08-03", "2021-09-05"],
               end=["2021-09-01", "2021-10-04", "2022-03-12"])

```

<br />

As a result a statistical table as well as graphical representation of the portfolio accumulated return will appear.

<br />

![1](https://user-images.githubusercontent.com/83161286/182113924-1510d4ac-a45f-47b7-a0f1-73451e0b38c3.png)


<br />

In order to access dataframe with portfolio daily changes and weights distribution, use:

<br />

```python
from plutus.backtest import execution

bt, portfolio_daily_changes, portfolio_weights = execution(asset=["AAPL", "TWTR", "GC=F"], 
                                                  start=["2021-08-01", "2021-08-03", "2021-09-05"],
                                                  end=["2021-09-01", "2021-10-04", "2022-03-12"])

portfolio_daily_changes.head()
```
<br />

The result will appear as following (all values are in %):

<br />

![port fin head](https://user-images.githubusercontent.com/83161286/178458212-9cd51033-707c-476c-a9ed-94c35255bb69.png)

<br />

If the user would like to compare performance of of the portfolio with any other instrument a parameter "benchmark" shall be called:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "TWTR", "FB"], start=["2021-08-01", "2021-08-03", "2021-09-05"],
               end =["2021-09-01", "2021-10-04", "2022-03-12"], benchmark= ['^GSPC'])

```
<br />

Above example will additionaly plot a S&P 500 index performance (accumulated return from same period as the portfolio) [grey line] on the accumulated graph:

<br />

![2](https://user-images.githubusercontent.com/83161286/182114014-c26376d5-93b7-4fb3-92c3-7d6d576118d4.png)

<br />

"Full report" is an optional parameter which allows users users to observe additional graphs frames and indicators:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "F", "MS"], 
              start=["2020-08-01", "2020-07-15", "2020-08-20"],
              end=["2021-09-01", "2021-09-01", "2021-09-15"], full_report = True)


```
<br />

Above script will generate a link to Dash app with report: 

<br />

![image](https://user-images.githubusercontent.com/83119547/175771957-67729f53-ef8e-43a1-b712-af079c401b1d.png)

<br />

By clicking it, and it will redirect to a new tab.

<br />

![127 0 0 1_8050_](https://user-images.githubusercontent.com/83161286/182018150-9e659433-b23f-4c16-a6c3-90261a7dafdf.png)

<br />

If the user didn't specify weights of particular assets in the portfolio (using **weights_factor** parameter), % allocation will be distributed equally (in selected period of time) and shown in the last plot called **Weights rebalancing**.

<br />

![127 0 0 1_8050_ (1)](https://user-images.githubusercontent.com/83161286/182018166-69e22ebf-e7b2-43a2-b9c8-cb63e627e68a.png)

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "F", "MS"],
              start=["2020-08-01", "2020-07-15", "2020-08-20"],
              end=["2021-09-01", "2021-09-01", "2021-09-15"],
              weights_factor = [50, 40, 10], full_report = True)

```

<br />

In case of specifying % of portfolio allocation for each asset (AAPL = 50%, F = 40%, MS = 10% from above example) above plots will be adjusted.
Example of Weights distribution plot:

<br />

![127 0 0 1_8050_ (2)](https://user-images.githubusercontent.com/83161286/182018187-2d2956fb-04f8-4e54-9ef4-d1477bc4aa66.png)

<br />

No need to include weights that will sum up to 100% (but it is recommended). Code calculates % based on **value / total of absolute values**. For example:

<br />

```python
from plutus.backtest import execution

bt = execution(asset=["AAPL", "F", "MS"],
              start=["2020-08-01", "2020-07-15", "2020-08-20"],
              end=["2021-09-01", "2021-09-01", "2021-09-15"],
              weights_factor = [35, 140, -21], full_report = True)
```

<br />

weights_factor total is 196 [35 + 140 + 21]. <br />
AAPL: 35 / 196 = ~17%<br />
F: 140 / 196 = ~71.4%<br />
MS: |21| / 196 = ~10.7%

Keep in mind that weights factor with "-" sign will indicate short selling for a particular asset

<br />

![127 0 0 1_8050_ (3)](https://user-images.githubusercontent.com/83161286/182018212-0459e3b7-675c-437a-b056-64880587c885.png)

<br />

More complex approach would be assigning weights factor/stop loss/ take profit indicators as well as adding brocker commission:

<br />

```python
from plutus.backtest import execution

bt = execution(asset = ["AAPL", "BTC-USD","GC=F"], 
              start = ["2021-08-01", "2021-07-15", "2021-08-20"],
              end = ["2021-09-01", "2021-09-01","2021-09-15"], 
              weights_factor = [10, -5, 35], 
              stop_loss = [0.8, 0.9, 0.95], 
              take_profit = [1.1, 1.2, 1.05], 
              full_report = True,broker_commission=0.01)

```

<br />

In this case the weights will not be distributed equally. "AAPL"  will have 20% of the total portofolio BTC-USD - 10% and 
"GC=F" will have 70%. The negative sign in the weights factor will mean short selling, therefore first "AAPL" and "GC=F" instruments are in long position and 
"BTC-USD" is in the short.

<br />

Stop loss and take profit shall be interpreted as "AAPL" has 20% of stop loss and 10% of take profit, "BTC-USD" has 10% of stop loss and 20% of take profit, "GC=F" 5% of stop loss and 5% of take profit. As result accumulative graph will look as:

<br />

![127 0 0 1_8050_ (4)](https://user-images.githubusercontent.com/83161286/182018278-9128864b-ce51-4507-86b2-0863dbcb67dc.png)

<br />

In the moment when one of the securities reaching its stop loss or take profit, the trade will be automatically stopped and the weights will be reassigned respectively to the left assets.

<br />

In case of users need to test one instrument but several times with different timelines, the package will interpret it as:

<br />

```python
from plutus.backtest import execution

bt, portfolio_daily_changes, pprtfolio_weights = execution(asset = ["AMZN", "AMZN","AMZN"], 
              start = ["2021-08-01", "2021-09-01", "2021-10-01"],
              end = ["2021-08-15", "2021-09-15","2021-10-15"])


```

<br />

![multiindex](https://user-images.githubusercontent.com/83161286/178458263-d0d4253a-5358-4876-862f-995fc8aaf134.png)

<br />

Each time when one asset is repeating the backtest will unite it under one comon ticker name, the same corrections will happen on the graphs. 
It's worth to mention that due to data limitation the code uses close price for the analysis of the securities. 

<br />



## Support:
Please [open an issue](https://github.com/witmul/backt/issues/new) for support.<br />
With additional questions please reachout to autors directly:
- [witmul](mailto:witalijmulawa@gmail.com)
- [IlliaBoloto](mailto:ils.boloto96@gmail.com)

