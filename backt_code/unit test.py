from backt_code.main import backtest

bt = backtest(["FDX", "APA", "MSFT"],
              ["2019-01-15", "2016-03-02", "2016-10-21"],
              ["2021-02-11", "2020-06-24", "2020-08-20"]) # max sell date is shown as max value -1 day



print(bt.consolidated())
print(bt.consolidated_detailed())

#Lube