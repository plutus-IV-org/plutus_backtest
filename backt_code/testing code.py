from backt_code.test_file import backtest



bt = backtest(["ATVI", "DXC", "APA"],
              ["2021-10-15", "2021-10-01", "2021-09-15"],
              ["2021-11-17", "2021-11-17", "2021-11-17"])

#weights_factor=[1,-3, 10], take_profit=[1.2, 1.05, 1.5], stop_loss=[0.9, 0.7, 0.8]
print(bt.ploting())

