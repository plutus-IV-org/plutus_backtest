from plutus_backtest.report import _report_generator
from plutus_backtest.puzzle_report import _puzzle_preparation, _puzzle_assembly, _puzzle_report_generator



# k = _report_generator(asset = ["AAPL", "BTC-USD", "TWTR"],
#                   o_day = ["2021-08-01", "2021-04-15", "2022-01-03"],
#                   c_day = ["2021-09-01", "2021-09-01", "2022-04-04"],
#                   benchmark="SPY")



bt1 = _puzzle_preparation(asset = ["AAPL", "BTC-USD","GC=F"],
               o_day = ["2021-08-01", "2021-07-15", "2021-08-20"],
               c_day = ["2021-09-01", "2021-09-01","2021-09-15"])

bt2 = _puzzle_preparation(asset = ["AMZN", "EURUSD=X"],
               o_day = ["2021-06-01", "2021-06-15"],
               c_day = ["2021-06-30", "2021-07-05"])

dic ={0:bt1, 1:bt2}

_puzzle_report_generator(_puzzle_assembly(dic))



# def generate_test(list_assets):
#     # --------------------------------------------------------- #
#     # START DATES GENERATION
#     min_year=2017
#     max_year=2017
#
#     start = datetime(min_year, 1, 1, 00, 00, 00)
#     years = max_year - min_year+1
#     end = start + timedelta(days=365 * years)
#
#     open_days = []
#
#     for i in range(len(list_assets)):
#         random_date = start + (end - start) * random.random()
#         open_days.append(random_date.strftime("%Y-%m-%d"))
#     # --------------------------------------------------------- #
#     # --------------------------------------------------------- #
#     # CLOSE DATES GENERATION
#     min_year=2021
#     max_year=2021
#
#     start = datetime(min_year, 1, 1, 00, 00, 00)
#     years = max_year - min_year+1
#     end = start + timedelta(days=365 * years)
#
#     close_days = []
#
#     for i in range(len(list_assets)):
#         random_date = start + (end - start) * random.random()
#         close_days.append(random_date.strftime("%Y-%m-%d"))
#     # --------------------------------------------------------- #
#     # --------------------------------------------------------- #
#     # WEIGHTS GENERATION (random numbers from 0 to 1 that sum to 1)
#     weights = ((np.random.dirichlet(np.ones(len(list_assets)),size=1))*100).tolist()[0]
#     # --------------------------------------------------------- #
#
#     bt = backtest(asset=list_assets, o_day=open_days, c_day=close_days,
#                   weights_factor=weights,
#                   price_period_relation="O-O",
#                   benchmark="F")