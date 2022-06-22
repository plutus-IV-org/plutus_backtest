from plutus_backtest import backtest
import pandas as pd
bt = backtest(asset=["AAPL", "BTC-USD", "GC=F"],
              o_day=["2021-08-01", "2021-07-15", "2021-08-20"],
              c_day=["2021-09-01", "2021-09-01", "2021-09-15"])

bt.plotting()
v =bt.capitlised_weights_distribution.to_excel('out1.xlsx')