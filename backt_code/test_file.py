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

# Adding one day to the latest
    def end_date(self):
        str_date = max(self.s_day)
        date = datetime.strptime(str_date, "%Y-%m-%d")
        modified_date = date + timedelta(days=1)
        back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")
        self.end_date = back_to_str

    def pricing(self):
        backtest.end_date(self)
        symbols = self.company_list['company'].values.tolist()
        data = yf.download(symbols, start=min(self.b_day), end=self.end_date, prepost = True)
        price = data[["Open", 'Adj Close']]
        price.index = price.index.strftime('%Y-%m-%d')
        self.price = price

    def consolidated_table_general(self):
        backtest.company_list(self)
        backtest.pricing(self)
        df_1 = self.company_list
        df_2 = self.price

        buy_list = []
        sell_list = []

        for com, b_d, s_d in zip(df_1["company"], df_1["buy day"], df_1["sell day"]):
            buy_list.append(df_2.loc[b_d, df_2.columns.get_level_values(1) == com]["Open"][0])
            sell_list.append(df_2.loc[s_d, df_2.columns.get_level_values(1) == com]["Adj Close"][0])

        df_1["buy price"] = buy_list
        df_1["sell price"] = sell_list
        self.general_return = df_1
        return self.general_return

    def consolidated_table_detailed(self):
        backtest.company_list(self)
        df_1 = self.company_list
        initial_df = pd.DataFrame()

        for com, b_d, s_d in zip(df_1["company"], df_1["buy day"], df_1["sell day"]):
            data = yf.download(com, start=b_d, end=s_d)
            data["Ticker"] = com
            initial_df = pd.concat([initial_df, data])

        df_close = initial_df[["Ticker", "Adj Close"]]
        df_close.columns = ['ticker', 'close_price']
        df_close_pivot = df_close.pivot_table(index=df_close.index, columns='ticker', values=['close_price'])
        df_close_pivot = df_close_pivot.replace([np.inf, -np.inf], np.nan)
        #df_close_pivot = df_close_pivot.fillna(method ="ffill")
        df_close_pivot = df_close_pivot.fillna(0)
        df_close_pivot = df_close_pivot.apply(pd.to_numeric)
        df_close_first_row = df_close_pivot.iloc[:1,:].values.tolist()


        df_open = initial_df[["Ticker", "Open"]]
        df_open.columns = ['ticker', 'open_price']
        df_open_pivot = df_open.pivot_table(index=df_open.index, columns='ticker', values=['open_price'])
        df_open_pivot = df_open_pivot.replace([np.inf, -np.inf], np.nan)
        #df_open_pivot = df_open_pivot.fillna(method="ffill")
        df_open_pivot = df_open_pivot.fillna(0)
        df_open_pivot = df_open_pivot.apply(pd.to_numeric)
        df_open_first_row = df_open_pivot.iloc[:1,:].values.tolist()

        df_daily_returns = df_close_pivot.pct_change()

        df_first_row_values = []
        for x, y in zip(df_close_first_row[0], df_open_first_row[0]):
            if y == 0:
                df_first_row_values.append(0)
            else:
                df_first_row_values.append((x / y) - 1)

        df_daily_returns.iloc[:1, :] = df_first_row_values
        df_daily_returns = df_daily_returns.replace([np.inf, -np.inf], np.nan)
        df_daily_returns = df_daily_returns.fillna(0)
        df_daily_returns = df_daily_returns.apply(pd.to_numeric)


        #Df for counting equal distributed weights
        self.auxiliar_df = df_close_pivot
        self.detailed_return = df_daily_returns
        return self.detailed_return

    def equal_weightining(self):
        binar_weights = self.auxiliar_df/self.auxiliar_df
        binar_weights.fillna(value=0, inplace = True)
        sum_of_binars = binar_weights.sum(axis=1)
        equal_distribution = binar_weights.div(sum_of_binars, axis = 0)
        self.equal_distribution = equal_distribution

    def portfolio_return_equal_wieghts(self):
        port_performance =self.equal_distribution * self.detailed_return
        port_performance['Sum'] = port_performance.sum(axis =1)
        port_performance['Sum'] = port_performance['Sum'] +1
        port_performance['Accumulation'] = port_performance['Sum'].cumprod()
        self.final_portfolio_frame = port_performance
        return self.final_portfolio_frame

    def ploting (self):
        backtest.consolidated_table_detailed(self)

        fig2 = plt.figure(figsize=(15, 7))
        ax2 = fig2.add_subplot(1, 1, 1)
        self.detailed_return["Cumulative return"].plot(ax=ax2)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Cumulative return')
        ax2.set_title('Portfolio Cumulative Returns')
        plt.show()


