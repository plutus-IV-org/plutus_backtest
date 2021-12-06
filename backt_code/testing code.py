import pandas as pd

from backt_code.test_file import backtest

dic = {}

bt = backtest(["ATVI", "DXC", "APA"],
              ["2020-10-15", "2020-10-01", "2020-09-15"],
              ["2020-11-17", "2020-11-17", "2020-11-17"])

bt2 = backtest(["NAVI", "SF", "DXC"],
              ["2021-10-15", "2021-10-01", "2021-09-15"],
              ["2021-11-17", "2021-11-17", "2021-11-17"])
bt.portfolio_construction()
bt2.portfolio_construction()
in_1 = bt.final_portfolio
in_2 = bt2.final_portfolio
dic[1]= in_1
dic[2]= in_2

bt.puzzle_assembly(dic)
