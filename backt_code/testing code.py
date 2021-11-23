from backt_code.test_file import backtest

bt = backtest(["ATVI", "DXC", "APA"],
              ["2021-10-15", "2021-10-01", "2021-09-15"],
              ["2021-11-17", "2021-11-17", "2021-11-17"])



print(bt.consolidated_table_detailed())
print(bt.equal_weightining())
print(bt.portfolio_return_equal_weights())
#print(bt.equal_weightining())
