import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


class backtest:
    def __init__(self, comp, b_day, s_day):
        self.comp = comp
        self.b_day = b_day
        self.s_day = s_day


    def company_list(self):
        df = pd.DataFrame({"company": self.comp,
                           "buy day": self.b_day,
                           "sell day": self.s_day})
        self.company_list = df

    def max_date(self):
        str_date = max(self.s_day)
        date = datetime.strptime(str_date, "%Y-%m-%d")
        modified_date = date + timedelta(days=1)
        back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")
        return back_to_str

    def pricing(self):
        backtest.company_list(self)
        symbols = self.company_list['company'].values.tolist()
        data = yf.download(symbols, start=min(self.b_day), end=backtest.max_date(self), prepost = True)
        price = data[["Open", 'Adj Close']]
        price.index = price.index.strftime('%Y-%m-%d')
        self.price = price


    def consolidated(self):
        backtest.pricing(self)
        df_1 = self.company_list
        df_2 = self.price

        buy_list = []
        sell_list = []

        for com, b_d, s_d in zip (df_1["company"], df_1["buy day"], df_1["sell day"]):
            buy_list.append(df_2.loc[b_d, df_2.columns.get_level_values(1) == com]["Open"][0])
            sell_list.append(df_2.loc[s_d, df_2.columns.get_level_values(1) == com]["Adj Close"][0])

        df_1["buy price"] = buy_list
        df_1["sell price"] = sell_list
        self.table = df_1
        return self.table


    def consolidated_detailed(self):
        backtest.consolidated(self)
        initial_df = pd.DataFrame()

        for com, b_d, s_d in zip(self.table["company"], self.table["buy day"], self.table["sell day"]):
            data = yf.download(com, start=b_d, end=s_d)
            data["Ticker"] = com
            initial_df = pd.concat([initial_df, data])

        df = initial_df[["Ticker", "Adj Close"]]
        df.columns = ['ticker', 'price']
        df1 = df.pivot_table(index=df.index, columns='ticker', values=['price'])

        df1 = df1.replace([np.inf, -np.inf], np.nan)
        df1 = df1.fillna(method = "ffill")
        df1 = df1.fillna(0)
        df1 = df1.apply(pd.to_numeric)

        df_daily_returns = df1.pct_change()

        df_daily_returns = df_daily_returns.replace([np.inf, -np.inf], np.nan)
        df_daily_returns = df_daily_returns.fillna(0)
        df_daily_returns = df_daily_returns.apply(pd.to_numeric)
        df_daily_returns["Total"] = df_daily_returns.sum(axis=1)
        df_daily_returns = df_daily_returns.iloc[1: , :]
        df_daily_returns["Cumulative return"] = (1 + df_daily_returns["Total"]).cumprod()

        self.detailed_return = df_daily_returns
        return self.detailed_return


    def ploting (self):
        backtest.consolidated_detailed(self)

        fig2 = plt.figure(figsize=(15, 7))
        ax2 = fig2.add_subplot(1, 1, 1)
        self.detailed_return["Cumulative return"].plot(ax=ax2)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Cumulative return')
        ax2.set_title('Portfolio Cumulative Returns')
        plt.show()


