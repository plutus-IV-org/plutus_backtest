from plutus.backtest import _report_generator
from plutus.puzzle_report import _puzzle_preparation, _puzzle_assembly, _puzzle_report_generator




bt1 = _puzzle_preparation(asset = ["AAPL", "BTC-USD","GC=F"],
               o_day = ["2021-08-01", "2021-07-15", "2021-08-20"],
               c_day = ["2021-09-01", "2021-09-01","2021-09-15"],
                          weights_factor = [10, 80, 10])

bt2 = _puzzle_preparation(asset = ["AMZN", "EURUSD=X"],
               o_day = ["2021-06-01", "2021-06-15"],
               c_day = ["2021-06-30", "2021-07-05"],
               weights_factor = [10, 90])

dic ={0:bt1, 1:bt2}

_puzzle_report_generator(_puzzle_assembly(dic))
