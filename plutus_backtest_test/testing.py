from plutus.backtest import execution
import pandas as pd
from datetime import datetime, timedelta
import random
import numpy as np


# k = _report_generator(asset = ["AAPL", "AAPL"],
#                   o_day = ["2021-08-02", "2021-08-16"],
#                   c_day = ["2021-08-10", "2021-08-20"])
#
# k = execution(asset=["AAPL", "TWTR", "GC=F"], o_day=["2021-08-01", "2021-08-03", "2021-09-05"],
#               c_day=["2021-09-01", "2021-10-04", "2022-03-12"], full_report=True)

df = pd.read_excel(r'C:\Users\ilsbo\PycharmProjects\plutus_backtest\plutus_backtest\sample_data_excel.xlsx')
k = execution(asset=df['Asset'], o_day=df['Open'], c_day=df['Close'], full_report= True)

# tickers = ["WMT", "V", "BAC", "KO", "PFE", "PEP", "CVX", "TWTR", "BX",
#            "PYPL", "SONY", "GE", "SBUX", "SBUX", "TEAM", "BSX",
#            "UBS", "GM", "DG", "TRP", "MRVL", "TRI", "SYY", "EC"]
#
#
# indexes = np.random.choice(len(tickers), 5, replace=True)
#
# cashe_list = []
# for x in indexes:
#     cashe_list.append(tickers[x])
#
# tickers_test = cashe_list
#
# def generate_test(list_of_tickers):
#     # --------------------------------------------------------- #
#     # START DATES GENERATION
#     min_year=2017
#     max_year=2020
#
#     start = datetime(min_year, 1, 1, 00, 00, 00)
#     years = max_year - min_year+1
#     end = start + timedelta(days=365 * years)
#
#     open_days = []
#
#     for i in range(len(list_of_tickers)):
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
#     for i in range(len(list_of_tickers)):
#         random_date = start + (end - start) * random.random()
#         close_days.append(random_date.strftime("%Y-%m-%d"))
#     # --------------------------------------------------------- #
#     # --------------------------------------------------------- #
#     # WEIGHTS GENERATION (random numbers from 0 to 1 that sum to 1)
#     weights = ((np.random.dirichlet(np.ones(len(list_of_tickers)),size=1))*100).tolist()[0]
#     # --------------------------------------------------------- #
#
#     bt = _report_generator(asset=list_of_tickers, o_day=open_days, c_day=close_days)
#
#
# generate_test(tickers_test)