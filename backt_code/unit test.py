from backt_code.main import backtest

bt = backtest(["ATVI", "DXC", "APA"],
              ["2021-11-15", "2021-11-15", "2021-11-15"],
              ["2021-11-17", "2021-11-17", "2021-11-17"])



print(bt.consolidated())
print(bt.consolidated_detailed())

#Lube