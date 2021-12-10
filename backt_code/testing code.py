import pandas as pd

from backt_code.main import backtest

dic = {}

bt = backtest(["ATVI", "DXC", "APA"],
              ["2020-10-15", "2020-10-01", "2020-09-15"],
              ["2020-11-17", "2021-11-17", "2021-11-17"])

bt2 = backtest(["NAVI", "SF", "DXC"],
              ["2020-10-15", "2021-10-01", "2021-09-15"],
              ["2021-11-17", "2021-11-17", "2021-12-08"])




# bt.plotting()

bt.portfolio_construction()
bt2.portfolio_construction()

in_1 = bt.final_portfolio
in_2 = bt2.final_portfolio

dic[1] = in_1
dic[2] = in_2

bt.puzzle_assembly(dic)



# import datetime
# a1 = datetime.datetime.now() - datetime.timedelta(20)
# a2 = datetime.datetime.now() - datetime.timedelta(30)
# a3 = datetime.datetime.now() - datetime.timedelta(50)
#
# b1 = a1 - datetime.timedelta(10)
# b2 = a2- datetime.timedelta(10)
# b3 = a3 - datetime.timedelta(10)
#
# c = [a1,a2,a3]
# o = [b1,b2,b3]
#
# bt = backtest(["ATVI", "DXC", "APA"],
#               o,
#               c)
# a =bt.portfolio_construction()
# a