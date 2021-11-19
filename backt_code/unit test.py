from backt_code.main import backtest

bt = backtest(["ATVI", "DXC", "APA"],
              ["2021-10-15", "2021-10-01", "2021-09-15"],
              ["2021-11-17", "2021-11-17", "2021-11-17"])



print(bt.consolidated())
print(bt.consolidated_detailed())
#print(bt.ploting())
#print(bt.equal_weightining())
