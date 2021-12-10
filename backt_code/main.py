import pandas as pd
import yfinance as yf
import numpy as np
import plotly.subplots as sp
import plotly.express as px
from datetime import datetime, timedelta



class backtest:
    """ :Parameters:

            comp: str or list
                Companies taken into the consideration for the backtest.
            o_day: list of str or timestamps
                Day/Days of the position opening.
            c_day: list of str or timestamps
                Day/Days of the position closing.
            weights_factor: int or float or array-like default None
                Optional list of factors which will be considered to define the weights for taken companies. By default
                all weights are distributed equally, however if the list of factors provided the backtest will maximize
                the weights towards the one with max weight factor. Negative weight factor will be considered as short selling.
            take_profit: float or int default None
                List of values determining the level till a particular stock shall be traded.
            stop_loss: float or int default None
                List of values determining the level till a particular stock shall be traded.
            """
    def __init__(self, comp, o_day, c_day, weights_factor= None , take_profit=None, stop_loss=None):
        self.comp = comp
        self.b_day = o_day
        self.s_day = c_day
        self.w_factor = weights_factor if weights_factor is not None else np.ones(len(comp))
        self.tp = take_profit if take_profit is not None else 100 * np.ones(len(comp))
        self.sl = stop_loss if stop_loss is not None else np.zeros(len(comp))

    def company_list(self):
        """
        :return:
            DataFrame with all input data.
        """
        df = pd.DataFrame({"company": self.comp,"start day": self.b_day,"end day": self.s_day,"weights factor": self.w_factor,
                           "take profit": self.tp,"stop loss": self.sl})
        df = df.set_index(df['company'])
        for x in df.index:
            if df.loc[x, "weights factor"] < 0:
                a = df.loc[x, "stop loss"]
                b = df.loc[x, "take profit"]
                df.loc[x,"take profit"] = (1-a) + 1
                df.loc[x,"stop loss"] = 1 - (b-1)
        self.company_list = df

# FOR DETAILED VIEW Adding one day to first buy and last sell dates
    def date_plus_one (self, d):
        str_date = d
        if type(str_date)== str:
            date = datetime.strptime(str_date, "%Y-%m-%d")
            modified_date = date + timedelta(days=1)
            back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")
        else:
            modified_date = str_date + timedelta(days=1)
            back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")

        return back_to_str

    def consolidated_table_detailed(self):
        backtest.company_list(self)
        df_1 = self.company_list
        initial_df = pd.DataFrame()

        for com, b_d, s_d in zip(df_1["company"], df_1["start day"], df_1["end day"]):
            data = yf.download(com, start=backtest.date_plus_one(self, b_d), end=backtest.date_plus_one(self, s_d))
            data["Ticker"] = com
            initial_df = pd.concat([initial_df, data])
        df_close = initial_df[["Ticker", "Adj Close"]]
        df_close.columns = ['ticker', 'close_price']
        df_open = initial_df[["Ticker", "Open"]]
        df_open.columns = ['ticker', 'open']
        open_price = df_open.groupby('ticker').first()
        em1 = pd.DataFrame()
        em2 =pd.DataFrame()
        for x in open_price.index:
            get_open = open_price.loc[x]
            get_end = df_close[df_close['ticker']==x]
            fake_df = pd.DataFrame(index=get_end.index, columns=['ticker', 'close_price'])
            fake_df = pd.DataFrame(fake_df.iloc[0]).T
            fake_df.iloc[0, 0] = x
            fake_df.iloc[0, 1] = get_open.values[0]
            merged_df = fake_df.append(get_end)
            merged_df['daily_change']=merged_df['close_price'].pct_change()
            merged_df = merged_df.iloc[1:]
            aux_df = merged_df[['ticker', 'close_price']]
            work_df = merged_df[['ticker', 'daily_change']]
            em1 = em1.append(aux_df)
            em2 = em2.append(work_df)
        dc = em2.pivot_table(index=em2.index, columns='ticker', values='daily_change')
        dc = dc[self.comp]
        dc = dc.replace([np.inf, -np.inf], np.nan)
        dc = dc.fillna(0)
        dc = dc.apply(pd.to_numeric)
        aux = em1.pivot_table(index=em2.index, columns='ticker', values='close_price')
        aux = aux[self.comp]
        aux = aux.replace([np.inf, -np.inf], np.nan)
        aux = aux.fillna(0)
        aux = aux.apply(pd.to_numeric)
        self.auxiliar_df = aux
        self.detailed_return = dc

        return self.detailed_return

    def portfolio_construction(self):
        """
        :return:
            Full constructed portfolio, including position length, weights factor, stop loss & take profit.
        """
        backtest.consolidated_table_detailed(self)
        binary_weights = self.auxiliar_df / self.auxiliar_df
        binary_weights.fillna(value=0, inplace=True)
        fac_summing = np.sum(abs(np.array(self.w_factor)))
        dist = np.array(self.w_factor) / fac_summing
        dist_df = pd.DataFrame(index= self.comp, data = self.w_factor).T
        weights_df = binary_weights * dist
        for z in weights_df.index:
            if abs(weights_df.loc[z]).sum()!=1:
                act = weights_df.loc[z][weights_df.loc[z]!=0]
                act_df = dist_df[act.index]
                new_dist =np.array(act_df)/np.sum(abs(np.array(act_df)))
                new_dist_frame = pd.DataFrame(columns = act.index, data = new_dist).T
                for i in new_dist_frame.index:
                    weights_df.loc[z,i] =float(new_dist_frame.loc[i].values)
        accu = (self.detailed_return + 1).cumprod()
        for x in accu.columns:
            q1 = accu[x]
            for y in q1:
                if y> self.company_list.loc[x, 'take profit']:
                    q1.iloc[q1.values.tolist().index(y)+1:] =0
                if y< self.company_list.loc[x, 'stop loss']:
                    q1.iloc[q1.values.tolist().index(y) + 1:] = 0
        aux_table_2 = accu* binary_weights
        new_binary_weights = aux_table_2/aux_table_2
        new_binary_weights.fillna(value=0, inplace=True)
        weights_df = new_binary_weights * dist
        for z in weights_df.index:
            if abs(weights_df.loc[z]).sum() != 1:
                act = weights_df.loc[z][weights_df.loc[z] != 0]
                act_df = dist_df[act.index]
                new_dist = np.array(act_df) / np.sum(abs(np.array(act_df)))
                new_dist_frame = pd.DataFrame(columns=act.index, data=new_dist).T
                for i in new_dist_frame.index:
                    weights_df.loc[z, i] = float(new_dist_frame.loc[i].values)
        port_performance = weights_df * self.detailed_return
        port_performance['Sum'] = port_performance.sum(axis=1)
        port_performance['Sum'] = port_performance['Sum'] + 1
        port_performance['Accumulation'] = port_performance['Sum'].cumprod()

        self.final_portfolio = port_performance

        return self.final_portfolio

    def plotting(self):
        """
        :return:
            Graphical repsresentaion of portfolio performance over given period.
        """
        df = backtest.portfolio_construction(self)
        # Monthly prod
        mon = []
        for x in self.final_portfolio.index:
            mon.append(x.strftime("%Y-%m"))
        months = set(mon)
        d = []
        v = []
        for x in months:
            n = self.final_portfolio.loc[x, 'Sum'].prod()
            d.append(x)
            v.append(n)
        com_frame = pd.DataFrame(index=d, data=v)
        com_frame = com_frame.sort_index()
        com_frame.index = pd.to_datetime(com_frame.index)
        com_frame.columns = ["Result"]

        #Need only to plot com_frame

        df = df.round(decimals=3)
        port_performance_drawdown = self.final_portfolio.copy()
        port_performance_drawdown = port_performance_drawdown.clip(upper=0)
        port_performance_drawdown = port_performance_drawdown.drop(columns = ['Sum', 'Accumulation'])
        port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
        port_performance_drawdown['Sum'] = port_performance_drawdown['Sum'] + 1
        port_performance_drawdown['Accumulation'] = port_performance_drawdown['Sum'].cumprod()
        self.drawdown = port_performance_drawdown
        df_drawdown = self.drawdown
        df_drawdown = df_drawdown.round(decimals=3)

        # Create figures in Express
        fig1 = px.line(df, x=df.index, y=df["Accumulation"],
                       hover_data=df.columns[:-2]) #show all columns values excluding last 2
        fig2 = px.line(df_drawdown, x=df_drawdown.index, y=df_drawdown["Accumulation"],
                       hover_data=df_drawdown.columns[:-2])

        fig3 = px.line(com_frame, x=com_frame.index, y=com_frame["Result"])

        # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
        # This is essentially breaking down the Express fig1 into it's traces

        figure1_traces = []
        figure2_traces = []
        figure3_traces = []

        for trace in range(len(fig1["data"])):
            figure1_traces.append(fig1["data"][trace])
        for trace in range(len(fig2["data"])):
            figure2_traces.append(fig2["data"][trace])
        for trace in range(len(fig3["data"])):
            figure3_traces.append(fig3["data"][trace])
        #Create a 1x3 subplot
        this_figure = sp.make_subplots(rows=3, cols=1)

        for traces in figure1_traces:
            this_figure.append_trace(traces, row=1, col=1)
        for traces in figure2_traces:
            this_figure.append_trace(traces, row=2, col=1)
        for traces in figure3_traces:
            this_figure.append_trace(traces, row=3, col=1)

        this_figure.update_layout(hovermode='x')
        this_figure.show()

    def general_statistic(self):
        backtest.portfolio_construction(self)
        obj = self.final_portfolio
        pdr = obj['Sum'] -1
        self.port_mean = pdr.mean()
        self.port_mean_pct = self.port_mean * 100
        self.port_std = pdr.std()
        self.LPM_0 = len(pdr[pdr<0])/len(pdr)
        self.LPM_1 = pdr.clip(upper=0).mean()
        self.LPM_2 = pdr.clip(upper=0).std()
        topless_pdr = pdr[pdr<self.port_std]
        botless_prd = topless_pdr[topless_pdr>-self.port_std]
        self.inner_mean = botless_prd.mean()
        obj_only_stocks =obj.drop(columns=['Sum', 'Accumulation'])
        self.stocks_mean = obj_only_stocks.mean()
        self.top_per = self.stocks_mean.nlargest(1)
        self.worst_per = self.stocks_mean.nsmallest(1)
        self.trade_length = len(pdr)
        VaR_95 = -1.65 * self.port_std * np.sqrt(self.trade_length)
        VaR_99 = -2.33 * self.port_std * np.sqrt(self.trade_length)
        CVaR = self.LPM_1/self.LPM_0
        print(f'Portfolio daily average return is {round(self.port_mean,2)}.')
        print(f'Portfolio standard deviation is {round(self.port_std, 2)}.')
        print(f'Daily average return for approximately 90% population is {round(self.inner_mean,2)}.')
        print(f'Downside daily probability is {round(self.LPM_0,2)}.')
        print(f'There is 95% confidence that you will not lose more than {round(100*VaR_95,2)} % of your portfolio in a given {self.trade_length} period.')
        print(f'There is 99% confidence that you will not lose more than {round(100*VaR_99,2)} % of your portfolio in a given {self.trade_length} period.')
        print(f'Expected loss that occur beyond the shortfall is {round(CVaR,4)}.')

    def puzzle_assembly(self, dic):
        """
        :param dic:
            dic: aggregated dictionary containing several constructed portfolios
        :return:
            Combines several backtests results into one graphical presentation.
        """


        names = dic.keys()
        empty_frame = pd.DataFrame()


        for x in names:
            q1 = dic[x][dic[x].columns[:-2]]
            empty_frame = empty_frame.append(q1)
        empty_frame = empty_frame.sort_index(ascending=True)
        empty_frame['Sum'] = (empty_frame.sum(axis=1)) + 1
        empty_frame['Accumulation'] = empty_frame['Sum'].cumprod()
        df = empty_frame.copy()
        df = df.round(decimals=3)
        df = df.fillna(0)
        port_performance_drawdown = df.copy()
        port_performance_drawdown = port_performance_drawdown.clip(upper=0)
        port_performance_drawdown = port_performance_drawdown.drop(columns=['Sum', 'Accumulation'])
        port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
        port_performance_drawdown['Sum'] = port_performance_drawdown['Sum'] + 1
        port_performance_drawdown['Accumulation'] = port_performance_drawdown['Sum'].cumprod()
        port_performance_drawdown = port_performance_drawdown.round(decimals=3)
        df_drawdown = port_performance_drawdown

        # Monthly prod
        mon = []
        for x in empty_frame.index:
            mon.append(x.strftime("%Y-%m"))
        months = set(mon)
        d = []
        v = []
        for x in months:
            n = empty_frame.loc[x, 'Sum'].prod()
            d.append(x)
            v.append(n)
        com_frame = pd.DataFrame(index=d, data=v)
        com_frame = com_frame.sort_index()
        com_frame.index = pd.to_datetime(com_frame.index)
        com_frame.columns = ["Result"]
        # Need only to plot com_frame

        # Create figures in Express
        fig1 = px.line(df, x=df.index, y=df["Accumulation"],
                       hover_data=df.columns[:-2])  # show all columns values excluding last 2
        fig2 = px.line(df_drawdown, x=df_drawdown.index, y=df_drawdown["Accumulation"],
                       hover_data=df_drawdown.columns[:-2])

        fig3 = px.line(com_frame, x=com_frame.index, y=com_frame["Result"])

        # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
        # This is essentially breaking down the Express fig1 into it's traces

        figure1_traces = []
        figure2_traces = []
        figure3_traces = []

        for trace in range(len(fig1["data"])):
            figure1_traces.append(fig1["data"][trace])
        for trace in range(len(fig2["data"])):
            figure2_traces.append(fig2["data"][trace])
        for trace in range(len(fig3["data"])):
            figure3_traces.append(fig3["data"][trace])
        # Create a 1x3 subplot
        this_figure = sp.make_subplots(rows=3, cols=1)

        for traces in figure1_traces:
            this_figure.append_trace(traces, row=1, col=1)
        for traces in figure2_traces:
            this_figure.append_trace(traces, row=2, col=1)
        for traces in figure3_traces:
            this_figure.append_trace(traces, row=3, col=1)

        this_figure.update_layout(hovermode='x')
        this_figure.show()

    def puzzle_statistic(self, dic):
        names = dic.keys()
        empty_frame = pd.DataFrame()
        for x in names:
            q1 = dic[x][dic[x].columns[:-2]]
            empty_frame = empty_frame.append(q1)

        empty_frame = empty_frame.sort_index(ascending=True)
        empty_frame['Sum'] = (empty_frame.sum(axis=1)) + 1
        empty_frame['Accumulation'] = empty_frame['Sum'].cumprod()
        pdr = empty_frame['Sum'] - 1
        port_mean = pdr.mean()
        port_mean_pct = port_mean * 100
        port_std = pdr.std()
        LPM_0 = len(pdr[pdr < 0]) / len(pdr)
        LPM_1 = pdr.clip(upper=0).mean()
        LPM_2 = pdr.clip(upper=0).std()
        topless_pdr = pdr[pdr < port_std]
        botless_prd = topless_pdr[topless_pdr > -port_std]
        inner_mean = botless_prd.mean()
        obj_only_stocks = empty_frame.drop(columns=['Sum', 'Accumulation'])
        stocks_mean = obj_only_stocks.mean()
        top_per = stocks_mean.nlargest(1)
        worst_per = stocks_mean.nsmallest(1)
        trade_length = len(pdr)
        VaR_95 = -1.65 * port_std * np.sqrt(trade_length)
        VaR_99 = -2.33 * port_std * np.sqrt(trade_length)
        CVaR = LPM_1 / LPM_0
        print(f'Portfolio daily average return is {round(port_mean, 2)}.')
        print(f'Portfolio standard deviation is {round(port_std, 2)}.')
        print(f'Daily average return for approximately 90% population is {round(inner_mean, 2)}.')
        print(f'Downside daily probability is {round(LPM_0, 2)}.')
        print(
            f'There is 95% confidence that you will not lose more than {round(100 * VaR_95, 2)} % of your portfolio in a given {trade_length} period.')
        print(
            f'There is 99% confidence that you will not lose more than {round(100 * VaR_99, 2)} % of your portfolio in a given {trade_length} period.')
        print(f'Expected loss that occur beyond the shortfall is {round(CVaR, 4)}.')