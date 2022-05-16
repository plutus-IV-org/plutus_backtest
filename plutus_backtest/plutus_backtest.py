import pandas as pd
import yfinance as yf
import numpy as np
import plotly.subplots as sp
import plotly.express as px
from datetime import datetime, timedelta
import sys
import matplotlib as plt
pd.options.mode.chained_assignment = None

########################
#Progress Bar functions#
########################

def start_progress(title):
    global progress_x
    sys.stdout.write(title + ": [")# + "-" * 40 + "]" + chr(8) * 41)
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x

def end_progress():
    sys.stdout.write("#" * (40 - progress_x) + "] DONE! \n\n")
    sys.stdout.flush()

######################
######## Code ########
######################

class backtest:
    """ :Parameters:

            asset: str or list or series
                Instruments taken into the consideration for the backtest.

            o_day: list of str or timestamps or series
                Day/Days of the position opening.

            c_day: list of str or timestamps or series
                Day/Days of the position closing.

            weights_factor: list of int or float or array-like or series default None
                Optional list of factors which will be considered to define the weights for taken companies. By default
                all weights are distributed equally, however if the list of factors provided the backtest will maximize
                the weights towards the one with max weight factor. Negative weight factor will be considered as short selling.

            take_profit: list of float or int or series default None
                List of values determining the level till a particular stock shall be traded.

            stop_loss: list of float or int or series default None
                List of values determining the level till a particular stock shall be traded.

            benchmark: str default None
                A benchmark ticker for comparison with portfolio performance

            price_period_relation: str default 'O-C'
                Instruct what part of the trading day a position shall be opened,
                and what part of trading day it shall be closed.
                Possible relations:
                O-C / Open to Close prices
                C-O / Close to Open prices
                C-C / Close to Close prices
                O-O / Open to Open prices
                "Open" - the price at which a security first trades upon the opening of an exchange on a trading day.
                "Close" - value of the last transacted price in a security before the market officially closes.
            """

    def __init__(self, asset, o_day, c_day, weights_factor=None, take_profit=None, stop_loss=None, benchmark=None,
                 price_period_relation=None):

        self.asset = asset
        self.b_day = o_day
        self.s_day = c_day
        self.w_factor = weights_factor if weights_factor is not None else np.ones(len(asset))
        self.tp = take_profit if take_profit is not None else len(self.asset) * [np.inf]
        self.sl = stop_loss if stop_loss is not None else len(self.asset) * [-np.inf]
        self.bench = benchmark

        if price_period_relation is None:
            self.p_p_p = "Open"
            self.p_p_n = "Adj Close"
        else:
            if price_period_relation == 'O-C':
                self.p_p_p = "Open"
                self.p_p_n = "Adj Close"
            elif price_period_relation == 'C-O':
                self.p_p_p = "Adj Close"
                self.p_p_n = "Open"
            elif price_period_relation == 'C-C':
                self.p_p_p = "Adj Close"
                self.p_p_n = "Adj Close"
            else:
                self.p_p_p = "Open"
                self.p_p_n = "Open"

    def benchmark_construction(self):
        backtest.security_list(self)
        min_date = min(self.security_list['start day'])
        max_date = max(self.security_list['end day'])
        df = yf.download(self.bench, start=backtest.date_plus_one(self, min_date),
                         end=backtest.date_plus_one(self, max_date), progress=False)
        df['Ticker'] = self.bench
        df_close = df[["Ticker", self.p_p_n]]
        df_close.columns = ['ticker', 'close_price']
        df_open = df[["Ticker", self.p_p_p]]
        df_open.columns = ['ticker', 'open']
        open_price = df_open.groupby('ticker').first()
        em1 = pd.DataFrame()
        em2 = pd.DataFrame()
        for x in open_price.index:
            get_open = open_price.loc[x]
            get_end = df_close[df_close['ticker'] == x]
            fake_df = pd.DataFrame(index=get_end.index, columns=['ticker', 'close_price'])
            fake_df = pd.DataFrame(fake_df.iloc[0]).T
            fake_df.iloc[0, 0] = x
            fake_df.iloc[0, 1] = get_open.values[0]
            merged_df = fake_df.append(get_end)
            merged_df['daily_change'] = merged_df['close_price'].pct_change()
            merged_df = merged_df.iloc[1:]
            aux_df = merged_df[['ticker', 'close_price']]
            work_df = merged_df[['ticker', 'daily_change']]
            em1 = em1.append(aux_df)
            em2 = em2.append(work_df)
        dc = em2.pivot_table(index=em2.index, columns='ticker', values='daily_change')
        dc = dc.replace([np.inf, -np.inf], np.nan)
        dc = dc.fillna(0)
        dc = dc.apply(pd.to_numeric)

        performance = dc
        performance['Bench_Sum'] = performance.sum(axis=1)
        performance['Bench_Sum'] = performance['Bench_Sum'] + 1
        performance['Bench_Accumulation'] = (performance['Bench_Sum'].cumprod() - 1) * 100
        performance.columns.name = None
        self.benchmark_performance = performance

        return self.benchmark_performance

    def security_list(self):
        """
        :return:
            DataFrame with all input data.
        """

        if isinstance(self.w_factor, pd.core.series.Series):
            self.w_factor = self.w_factor.values
        if isinstance(self.b_day, pd.core.series.Series):
            self.b_day = self.b_day.values
        if isinstance(self.s_day, pd.core.series.Series):
            self.s_day = self.s_day.values
        if isinstance(self.asset, pd.core.series.Series):
            self.asset = self.asset.values
        if isinstance(self.tp, pd.core.series.Series):
            self.tp = self.tp.values
        if isinstance(self.sl, pd.core.series.Series):
            self.sl = self.sl.values

        df = pd.DataFrame(
            {"company": self.asset, "start day": self.b_day, "end day": self.s_day, "weights factor": self.w_factor,
             "take profit": self.tp, "stop loss": self.sl})
        df = df.set_index(df['company'])
        for x in range(len(df.index)):
            if df.iloc[x, 3] < 0 and df.iloc[x, 4]!= np.inf and df.iloc[x,5]!= -np.inf:
                a = df.iloc[x, 5]
                b = df.iloc[x, 4]
                df.iloc[x, 4] = (1 - a) + 1
                df.iloc[x, 5] = 1 - (b - 1)

            if df.iloc[x, 3] < 0 and df.iloc[x, 4]!= np.inf and df.iloc[x,5]== -np.inf:
                b = df.iloc[x, 4]
                df.iloc[x, 4] = 100500
                df.iloc[x, 5] = 1 - (b - 1)

            if df.iloc[x, 3] < 0 and df.iloc[x, 4]== np.inf and df.iloc[x,5]!= -np.inf:
                a = df.iloc[x, 5]
                df.iloc[x, 4] = (1 - a) + 1
                df.iloc[x, 5] = -100500
        df = df.replace(100500, np.inf)
        df = df.replace(-100500, np.inf)
        self.security_list = df
        return self.security_list

    def date_plus_one(self, d):
        str_date = d
        if type(str_date) == str:
            date = datetime.strptime(str_date, "%Y-%m-%d")
            modified_date = date + timedelta(days=1)
            back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")
            return back_to_str
        else:
            modified_date = str_date + timedelta(days=1)
            back_to_str = datetime.strftime(modified_date, "%Y-%m-%d")
            return back_to_str

    def consolidated_table_detailed(self):

        backtest.security_list(self)

        start_progress("Consolidating detailed table: ")

        df_1 = self.security_list
        initial_df = pd.DataFrame()
        fq = pd.DataFrame(index=self.asset, data=self.b_day)
        # check if companies are dublicatted in a list
        v = fq.groupby(fq.index) \
            .cumcount()
        # doubled companies will have suffix
        list_new = []
        for x in range(len(v.values)):
            if v.iloc[x] != 0:
                a2 = v.index[x] + str(v.iloc[x])
                list_new.append(a2)
            else:
                list_new.append(v.index[x])
        min_date = min(self.security_list['start day'])
        max_date = max(self.security_list['end day'])
        ydata = yf.download(self.asset, start=backtest.date_plus_one(self, min_date),
                            end=backtest.date_plus_one(self, max_date), progress=False)
        if ydata.empty:
            raise ValueError('No trading days were provided, perhaps days off or holidays have been given')
        #check if column names are Multiindex
        if not isinstance(ydata.columns, pd.MultiIndex):
        #select desired start / end dates for selected companies
            for b_d, s_d, new_com in zip(df_1["start day"], df_1["end day"], list_new):
                data = ydata.loc[b_d:s_d]
                data['Ticker'] = new_com
                initial_df = pd.concat([initial_df, data])
        else:
            for com, b_d, s_d, new_com in zip(df_1["company"], df_1["start day"], df_1["end day"], list_new):
                q1 = ydata.iloc[:, ydata.columns.get_level_values(1) == com]
                q1.columns = q1.columns.droplevel(1)
                data = q1.loc[b_d:s_d]
                data['Ticker'] = new_com
                initial_df = pd.concat([initial_df, data])
        df_close = initial_df[["Ticker", self.p_p_n]]
        df_close.columns = ['ticker', 'close_price']
        df_open = initial_df[["Ticker", self.p_p_p]]
        df_open.columns = ['ticker', 'open']
        open_price = df_open.groupby('ticker').first()
        em1 = pd.DataFrame()
        em2 = pd.DataFrame()

        progress(50)

        for x in open_price.index:
            get_open = open_price.loc[x]
            get_end = df_close[df_close['ticker'] == x]
            fake_df = pd.DataFrame(index=get_end.index, columns=['ticker', 'close_price'])
            fake_df = pd.DataFrame(fake_df.iloc[0]).T
            fake_df.iloc[0, 0] = x
            fake_df.iloc[0, 1] = get_open.values[0]
            merged_df = pd.concat([fake_df, get_end])
            merged_df['daily_change'] = merged_df['close_price'].pct_change()
            merged_df = merged_df.iloc[1:]
            aux_df = merged_df[['ticker', 'close_price']]
            work_df = merged_df[['ticker', 'daily_change']]
            em1 = pd.concat([em1, aux_df])
            em2 = pd.concat([em2, work_df])

        dc = em2.pivot_table(index=em2.index, columns='ticker', values='daily_change')
        self.asset = list_new
        backtest.security_list(self)
        if dc.columns.tolist() != self.asset:
            l1 = dc.columns.tolist()
            l2 = self.asset
            res = [x for x in l1 + l2 if x not in l1 or x not in l2]
            self.asset = l1
            self.security_list = self.security_list.drop(res)
            self.b_day = self.security_list['start day'].values
            self.s_day = self.security_list['end day'].values
            self.w_factor = self.security_list['weights factor'].values
            self.sl = self.security_list['stop loss'].values
            self.tp = self.security_list['take profit'].values
            if res ==[]:
                pass
            else:
                print(f"\nNo price data found for {res} therefore was deleted from provided inputs.\n")

        dc = dc[self.security_list['company']]
        dc = dc.replace([np.inf, -np.inf], np.nan)
        dc = dc.fillna(0)
        dc = dc.apply(pd.to_numeric)
        aux = em1.pivot_table(index=em2.index, columns='ticker', values='close_price')
        aux = aux[self.security_list['company']]
        aux = aux.replace([np.inf, -np.inf], np.nan)
        aux = aux.fillna(0)
        aux = aux.apply(pd.to_numeric)
        self.auxiliar_df = aux
        self.detailed_return = dc

        progress(50)
        end_progress()

        return self.detailed_return

    def portfolio_construction(self):
        """
        :return:
            Full constructed portfolio, including position length, weights factor, stop loss & take profit.
        """

        backtest.consolidated_table_detailed(self)

        start_progress("Constructing your portfolio: ")

        binary_weights = self.auxiliar_df / self.auxiliar_df
        binary_weights.fillna(value=0, inplace=True)
        fac_summing = np.sum(abs(np.array(self.w_factor)))
        dist = np.array(self.w_factor) / fac_summing
        dist_df = pd.DataFrame(index=self.security_list['company'], data=self.w_factor).T
        weights_df = binary_weights * dist

        progress(25)

        for z in weights_df.index:
            if abs(weights_df.loc[z]).sum() != 1:
                act = weights_df.loc[z][weights_df.loc[z] != 0]
                act_df = dist_df[act.index]
                new_dist = np.array(act_df) / np.sum(abs(np.array(act_df)))
                new_dist_frame = pd.DataFrame(columns=act.index, data=new_dist).T
                for i in new_dist_frame.index:
                    weights_df.loc[z, i] = float(new_dist_frame.loc[i].values)
        accu = (self.detailed_return + 1).cumprod()
        for x in accu.columns:
            q1 = accu[x]
            for y in q1:
                if y > self.security_list.loc[x, 'take profit']:
                    q1.iloc[q1.values.tolist().index(y) + 1:] = 0
                if y < self.security_list.loc[x, 'stop loss']:
                    q1.iloc[q1.values.tolist().index(y) + 1:] = 0
        aux_table_2 = accu * binary_weights
        new_binary_weights = aux_table_2 / aux_table_2
        new_binary_weights.fillna(value=0, inplace=True)
        weights_df = new_binary_weights * dist

        progress(25)

        for z in weights_df.index:
            if abs(weights_df.loc[z]).sum() != 1:
                act = weights_df.loc[z][weights_df.loc[z] != 0]
                act_df = dist_df[act.index]
                new_dist = np.array(act_df) / np.sum(abs(np.array(act_df)))
                new_dist_frame = pd.DataFrame(columns=act.index, data=new_dist).T
                for i in new_dist_frame.index:
                    weights_df.loc[z, i] = float(new_dist_frame.loc[i].values)
        port_performance = weights_df * self.detailed_return
        aux_table_3 = weights_df.copy()
        aux_table_3[aux_table_3<0]=-1
        aux_table_3[aux_table_3>0]=1
        dc1 = (self.detailed_return * aux_table_3 + 1)
        dc2 = dc1 * abs(weights_df)
        port_performance['Sum'] = port_performance.sum(axis=1)
        port_performance['Sum'] = port_performance['Sum'] + 1
        port_performance['Accumulation'] = (port_performance['Sum'].cumprod() - 1) * 100
        aux_series = port_performance.Sum.cumprod()
        aux_series_2 = aux_series.shift().fillna(value = 1)
        dc2 =(dc2.T * aux_series_2).T
        dc2['Accu'] = aux_series
        self.capitlised_weights_distribution = dc2

        progress(25)

        q1 = port_performance.index[0] - timedelta(days=1)  # starting from 0%
        port_performance.loc[q1] = [0] * len(port_performance.columns)
        port_performance = port_performance.sort_index()

        self.final_portfolio = port_performance
        self.portfolio_weights = weights_df

        # small addition to be able to show a table
        execution_table = self.final_portfolio.astype(float)
        execution_table.iloc[:, :-2] = (execution_table.iloc[:, :-2] * 100)
        execution_table.drop('Sum', axis=1, inplace=True)
        self.execution_table = execution_table.round(2)

        progress(25)
        end_progress()

    def execution(self):
        """
        :return:
            Backtest statistic and cumulative return of the given portfolio.
        """
        # ----------------------------------------------------------------------- #
        # Stats
        try:
            df_execution = self.final_portfolio
        except:
            backtest.portfolio_construction(self)
            df_execution = self.final_portfolio

        start_progress("Working on results: ")
        progress(50)

        df_execution = df_execution.round(decimals=3)
        obj = self.final_portfolio
        pdr = obj['Sum'] - 1
        self.port_mean = pdr.mean()
        self.port_mean_pct = self.port_mean * 100
        self.port_std = pdr.std()
        self.LPM_0 = len(pdr[pdr < 0]) / len(pdr)
        self.LPM_1 = pdr.clip(upper=0).mean()
        self.LPM_2 = pdr.clip(upper=0).std()
        if self.LPM_0 == 0:
            self.LPM_0 = 0.01
        topless_pdr = pdr[pdr < self.port_std]
        botless_prd = topless_pdr[topless_pdr > -self.port_std]
        self.inner_mean = botless_prd.mean()
        obj_only_stocks = obj.drop(columns=['Sum', 'Accumulation'])
        self.stocks_mean = obj_only_stocks.mean()
        self.top_per = self.stocks_mean.nlargest(1)
        self.worst_per = self.stocks_mean.nsmallest(1)
        self.trade_length = len(pdr) - 1
        VaR_95 = -1.65 * self.port_std * np.sqrt(self.trade_length)
        VaR_99 = -2.33 * self.port_std * np.sqrt(self.trade_length)
        CVaR = self.LPM_1 / self.LPM_0
        list_1 = ['Mean', 'Std', 'Downside prob', 'Downside mean', 'Downside std', 'Investment period', 'VaR_95',
                  'VaR_99', 'CVaR']
        list_2 = [self.port_mean, self.port_std, self.LPM_0, self.LPM_1, self.LPM_2, self.trade_length, VaR_95, VaR_99,
                  CVaR]
        frame = pd.DataFrame({'Indicators': list_1, 'Values': list_2})
        self.stat_frame = frame
        frame = frame.to_string(index=False)


        # ----------------------------------------------------------------------- #
        # Execution plot - 2 ways


        if self.bench is not None:
            df_bench = backtest.benchmark_construction(self)
            df_execution = pd.merge(df_execution, df_bench["Bench_Accumulation"], how='right', left_index=True,
                                    right_index=True)
            df_execution["Bench_Accumulation"] = df_execution["Bench_Accumulation"].fillna(method='ffill')
            df_execution['Accumulation'] = df_execution['Accumulation'].ffill()
            df_execution.fillna(value = 0 , inplace = True)
            # Execution plot - Accumulation with benchmark
            df_execution_fig1 = df_execution.astype(float)
            df_execution_fig1.iloc[:, :-2] = (df_execution_fig1.iloc[:, :-2] * 100)
            df_execution_fig1 = df_execution_fig1.round(2)
            df_execution_fig1 = df_execution_fig1.fillna(0)

            fig1 = px.line(df_execution_fig1,
                           x=df_execution_fig1.index,
                           y=df_execution_fig1["Accumulation"],
                           title="Accumulated return",
                           hover_data=df_execution_fig1.columns[:-3])  # show all columns values excluding last 3

            fig1.update_layout(xaxis_title="Date")
            fig1.update_traces(name='Portfolio',
                               showlegend=True)

            fig1.add_scatter(x=df_execution_fig1.index,
                             y=df_execution_fig1["Bench_Accumulation"],
                             mode='lines',
                             name="Benchmark")

            fig1.update_yaxes(tickprefix="%")

            progress(50)
            end_progress()

            print(frame)

            fig1.show()

        else:

            # Execution plot - Accumulation no benchmark
            df_execution_fig1 = df_execution.astype(float)
            df_execution_fig1.iloc[:, :-2] = (df_execution_fig1.iloc[:, :-2] * 100)
            df_execution_fig1 = df_execution_fig1.round(2)
            fig1 = px.line(df_execution_fig1,
                           x=df_execution_fig1.index,
                           y=df_execution_fig1["Accumulation"],
                           title="Accumulated return",
                           hover_data=df_execution_fig1.columns[:-2])  # show all columns values excluding last 2
            fig1.update_layout(xaxis_title="Date")
            fig1.update_yaxes(tickprefix="%")

            progress(50)
            end_progress()

            print(frame)

            fig1.show()

    def plotting(self):
        """
        :return:
            Graphical repsresentaion of portfolio performance over the given period.
        """

        try:
            df_accum = self.final_portfolio.copy()
        except:
            backtest.portfolio_construction(self)
            df_accum = self.final_portfolio.copy()

        start_progress("Working on plots: ")

        progress(20)

        # ----------------------------------------------------------------------- #
        # Stats
        obj = self.final_portfolio.copy()
        obj = obj.drop(index=obj.index[0], axis=0)  # drop first row which is 0

        pdr = obj['Sum'] - 1
        self.port_mean = pdr.mean()
        self.port_mean_pct = self.port_mean * 100
        self.port_std = pdr.std()
        self.LPM_0 = len(pdr[pdr < 0]) / len(pdr)
        self.LPM_1 = pdr.clip(upper=0).mean()
        self.LPM_2 = pdr.clip(upper=0).std()
        if self.LPM_0 == 0:
            self.LPM_0 = 0.01
        topless_pdr = pdr[pdr < self.port_std]
        botless_prd = topless_pdr[topless_pdr > -self.port_std]
        self.inner_mean = botless_prd.mean()
        obj_only_stocks = obj.drop(columns=['Sum', 'Accumulation'])
        self.stocks_mean = obj_only_stocks.mean()
        self.top_per = self.stocks_mean.nlargest(1)
        self.worst_per = self.stocks_mean.nsmallest(1)
        self.trade_length = len(pdr) - 1
        VaR_95 = -1.65 * self.port_std * np.sqrt(self.trade_length)
        VaR_99 = -2.33 * self.port_std * np.sqrt(self.trade_length)
        CVaR = self.LPM_1 / self.LPM_0

        # ----------------------------------------------------------------------- #
        # Drawdown
        progress(20)

        port_performance_drawdown = self.final_portfolio.copy()
        port_performance_drawdown = port_performance_drawdown.clip(upper=0)
        port_performance_drawdown = port_performance_drawdown.drop(columns=['Sum', 'Accumulation'])
        # port_performance_drawdown = abs(port_performance_drawdown)
        port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
        port_performance_drawdown['Accumulation'] = (port_performance_drawdown['Sum'].cumsum()) * 100
        df_drawdown = port_performance_drawdown
        df_drawdown = df_drawdown.round(decimals=3)

        # ----------------------------------------------------------------------- #
        # Monthly prod
        progress(20)

        mon = []
        df_monthly = self.final_portfolio.copy()
        df_monthly = df_monthly.drop(index=df_monthly.index[0], axis=0)  # drop first row

        for x in df_monthly.index:
            mon.append(x.strftime("%Y-%m"))
        months = set(mon)
        d = []
        v = []
        for x in months:
            n = (df_monthly.loc[x, 'Sum'].prod() - 1) * 100
            d.append(x)
            v.append(n)
        com_frame = pd.DataFrame(index=d, data=v)
        com_frame = com_frame.sort_index()
        com_frame.index = com_frame.index.map(str)
        # com_frame.index = pd.to_datetime(com_frame.index)
        df_montly = com_frame
        df_montly.columns = ["Result"]

        # ----------------------------------------------------------------------- #
        # Create figures in Express
        progress(20)

        # ----------------------------------------------------------------------- #
        # Add benchmark if triggered

        if self.bench is not None:
            df_bench = backtest.benchmark_construction(self)
            df_accum = pd.merge(df_accum.copy(), df_bench["Bench_Accumulation"], how='right', left_index=True,
                                right_index=True)
            #df_accum = df_accum.fillna(0)
            df_accum["Bench_Accumulation"] = df_accum["Bench_Accumulation"].fillna(method='ffill')
            df_accum['Accumulation'] = df_accum['Accumulation'].ffill()
            df_accum.fillna(value=0, inplace=True)
            # Execution plot - Accumulation with benchmark
            df_accum_fig1 = df_accum.astype(float)
            df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
            df_accum_fig1 = df_accum_fig1.round(2)
            df_accum_fig1 = df_accum_fig1.fillna(0)

            fig1 = px.line(df_accum_fig1,
                           x=df_accum_fig1.index,
                           y=df_accum_fig1["Accumulation"],
                           title="Accumulated return",
                           hover_data=df_accum_fig1.columns[:-3])  # show all columns values excluding last 3

            fig1.update_layout(xaxis_title="Date")
            fig1.update_traces(name='Portfolio',
                               showlegend=True)

            fig1.add_scatter(x=df_accum_fig1.index,
                             y=df_accum_fig1["Bench_Accumulation"],
                             mode='lines',
                             name="Benchmark")
        else:

            df_accum_fig1 = df_accum.astype(float)
            df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
            df_accum_fig1 = df_accum_fig1.round(2)
            fig1 = px.line(df_accum_fig1,
                           x=df_accum_fig1.index,
                           y=df_accum_fig1["Accumulation"],
                           hover_data=df_accum_fig1.columns[:-2])  # show all columns values excluding last 2


        weights_df = self.portfolio_weights
        weights_df["Total Weights"] = weights_df.sum(axis=1)
        weights_df = weights_df[weights_df["Total Weights"] != 0]
        weights_df = weights_df.drop("Total Weights", axis=1)
        weights_df = abs(weights_df)
        fig2 = px.area(weights_df * 100,
                       x=weights_df.index,
                       y=weights_df.columns)

        df_montly_fig3 = df_montly.astype(float)
        color = []
        for i in df_montly_fig3["Result"]:
            if i < 0:
                color.append('red')
            else:
                color.append('green')
        df_montly_fig3["color"] = color
        df_montly_fig3 = df_montly_fig3.round(2)
        fig3 = px.bar(df_montly_fig3,
                      x=df_montly_fig3.index,
                      y=df_montly_fig3["Result"],
                      color=df_montly_fig3["color"],
                      color_discrete_sequence=df_montly_fig3["color"].unique())

        df_drawdown_fig2 = df_drawdown.astype(float)
        df_drawdown_fig2.iloc[:, :-2] = (df_drawdown_fig2.iloc[:, :-2] * 100)
        df_drawdown_fig2 = df_drawdown_fig2.round(2)
        fig4 = px.line(df_drawdown_fig2,
                       x=df_drawdown_fig2.index,
                       y=df_drawdown_fig2["Sum"] * 100,
                       hover_data=df_drawdown_fig2.columns[:-2])  # show all columns values excluding last 2

        # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
        # This is essentially breaking down the Express fig1, 2, 3 into it's traces
        figure1_traces = []
        figure2_traces = []
        figure3_traces = []
        figure4_traces = []

        for trace in range(len(fig1["data"])):
            figure1_traces.append(fig1["data"][trace])

        for trace in range(len(fig2["data"])):
            figure2_traces.append(fig2["data"][trace])

        for trace in range(len(fig3["data"])):
            figure3_traces.append(fig3["data"][trace])

        for trace in range(len(fig4["data"])):
            figure4_traces.append(fig4["data"][trace])

        # Create a 1x4 subplot
        this_figure = sp.make_subplots(rows=4, cols=1,
                                       vertical_spacing=0.1,
                                       shared_xaxes=False,
                                       shared_yaxes=False,
                                       subplot_titles=("Accumulative return",
                                                       "Weights distribution",
                                                       "Monthly return",
                                                       "Drawdown"
                                                       ))

        for traces in figure1_traces:
            this_figure.append_trace(traces, row=1, col=1)

        for traces in figure2_traces:
            this_figure.append_trace(traces, row=2, col=1)

        for traces in figure3_traces:
            this_figure.append_trace(traces, row=3, col=1)

        for traces in figure4_traces:
            this_figure.append_trace(traces, row=4, col=1)

        this_figure.update_layout(hovermode='x', showlegend=False)
        # Prefix y-axis tick labels with % sign
        this_figure.update_yaxes(tickprefix="%")
        this_figure['layout'].update(height=1400, title='Plotting results')

        progress(20)
        end_progress()

        # ----------------------------------------------------------------------- #
        # Printing stats

        print(f'Portfolio daily average return is {round(self.port_mean, 2)}.')
        print(f'Portfolio standard deviation is {round(self.port_std, 2)}.')
        print(f'Daily average return for approximately 90% population is {round(self.inner_mean, 2)}.')
        print(f'Downside daily probability is {round(self.LPM_0, 2)}.')
        print(
            f'There is 95% confidence that you will not lose more than {round(100 * VaR_95, 2)} % of your portfolio in a given {self.trade_length} period.')
        print(
            f'There is 99% confidence that you will not lose more than {round(100 * VaR_99, 2)} % of your portfolio in a given {self.trade_length} period.')
        print(f'Expected loss that occur beyond the shortfall is {round(CVaR, 4)}.')

        # ----------------------------------------------------------------------- #
        # Printing plots

        this_figure.show()

    def puzzle_assembly(dic):
        """
        :param:
            dic: aggregated dictionary containing several constructed portfolios
        :return:
            Combines several backrests results into one dataframe
        """
        start_progress("Compiling your puzzle: ")

        progress(50)

        names = dic.keys()
        empty_frame = pd.DataFrame()
        for x in names:
            q1 = dic[x][dic[x].columns[:-2]]
            empty_frame = empty_frame.append(q1)
        empty_frame = empty_frame.sort_index(ascending=True)
        empty_frame['Sum'] = (empty_frame.sum(axis=1)) + 1
        empty_frame['Accumulation'] = (empty_frame['Sum'].cumprod() - 1) * 100
        empty_frame = empty_frame.fillna(0)
        empty_frame = empty_frame.astype(float)
        empty_frame = empty_frame.round(4)

        progress(50)
        end_progress()

        return empty_frame

    def puzzle_execution(data):
        """
        :param:
            data: aggregated dataframe from several backtests
        :return:
            Combined backtests statistic and cumulative return of the portfolio
        """
        start_progress("Working on puzzle results: ")

        empty_frame = data
        empty_frame = empty_frame.round(decimals=3)
        empty_frame = empty_frame.fillna(0)
        q1 = empty_frame.iloc[:, :-2]
        q2 = sum(abs(q1).sum(axis=1) == 0)
        # ----------------------------------------------------------------------- #
        # Stats
        progress(50)

        pdr = empty_frame['Sum'] - 1
        port_mean = pdr.mean()
        port_std = pdr.std()
        LPM_0 = len(pdr[pdr < 0]) / len(pdr)
        LPM_1 = pdr.clip(upper=0).mean()
        LPM_2 = pdr.clip(upper=0).std()
        if LPM_0 == 0:
            LPM_0 = 0.01
        trade_length = len(pdr) - q2
        VaR_95 = -1.65 * port_std * np.sqrt(trade_length)
        VaR_99 = -2.33 * port_std * np.sqrt(trade_length)
        CVaR = LPM_1 / LPM_0
        list_1 = ['Mean', 'Std', 'Downside prob', 'Downside mean', 'Downside std', 'Investment period', 'VaR_95',
                  'VaR_99', 'CVaR']
        list_2 = [port_mean, port_std, LPM_0, LPM_1, LPM_2, trade_length, VaR_95, VaR_99,
                  CVaR]
        frame = pd.DataFrame({'Indicators': list_1, 'Values': list_2})
        frame = frame.to_string(index=False)

        # ----------------------------------------------------------------------- #
        # Execution plot - Accumulation
        progress(50)

        df_execution_fig1 = empty_frame.astype(float)
        df_execution_fig1.iloc[:, :-2] = (df_execution_fig1.iloc[:, :-2] * 100)
        df_execution_fig1 = df_execution_fig1.round(2)
        fig1 = px.line(df_execution_fig1,
                       x=df_execution_fig1.index,
                       y=df_execution_fig1["Accumulation"],
                       title="Puzzle accumulated return",
                       hover_data=df_execution_fig1.columns[:-2])  # show all columns values excluding last 2
        fig1.update_layout(xaxis_title="Date")
        fig1.update_yaxes(tickprefix="%")

        # ----------------------------------------------------------------------- #
        # Printing stats
        end_progress()
        print(frame)

        # ----------------------------------------------------------------------- #
        # Printing plots

        fig1.show()

    def puzzle_plotting(data):
        """
        :param:
            data: aggregated dataframe from several backtests
        :return:
            Combines several backtests results into graphical representations
        """

        start_progress("Working on puzzle plots: ")

        df = data
        df = df.round(decimals=3)
        df = df.fillna(0)

        progress(20)

        # ----------------------------------------------------------------------- #
        # Stats
        empty_frame = df
        q1 = empty_frame.iloc[:, :-2]
        q2 = sum(abs(q1).sum(axis=1) == 0)
        pdr = empty_frame['Sum'] - 1
        port_mean = pdr.mean()
        port_std = pdr.std()
        LPM_0 = len(pdr[pdr < 0]) / len(pdr)
        LPM_1 = pdr.clip(upper=0).mean()
        LPM_2 = pdr.clip(upper=0).std()
        if LPM_0 == 0:
            LPM_0 = 0.01
        trade_length = len(pdr) - q2
        VaR_95 = -1.65 * port_std * np.sqrt(trade_length)
        VaR_99 = -2.33 * port_std * np.sqrt(trade_length)
        CVaR = LPM_1 / LPM_0
        list_1 = ['Mean', 'Std', 'Downside prob', 'Downside mean', 'Downside std', 'Investment period', 'VaR_95',
                  'VaR_99', 'CVaR']
        list_2 = [port_mean, port_std, LPM_0, LPM_1, LPM_2, trade_length, VaR_95, VaR_99,
                  CVaR]
        frame = pd.DataFrame({'Indicators': list_1, 'Values': list_2})
        frame = frame.to_string(index=False)

        # ----------------------------------------------------------------------- #
        # Drawdown
        progress(20)

        port_performance_drawdown = df.copy()
        port_performance_drawdown = port_performance_drawdown.clip(upper=0)
        port_performance_drawdown = port_performance_drawdown.drop(columns=['Sum', 'Accumulation'])
        #port_performance_drawdown = abs(port_performance_drawdown)
        port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
        port_performance_drawdown['Accumulation'] = (port_performance_drawdown['Sum'].cumsum()) * 100
        df_drawdown = port_performance_drawdown
        df_drawdown = df_drawdown.round(decimals=3)

        # ----------------------------------------------------------------------- #
        # Monthly prod
        progress(20)

        mon = []
        df_monthly = df.copy()
        df_monthly = df_monthly.drop(index=df.index[0], axis=0)  # drop first row

        for x in df_monthly.index:
            mon.append(x.strftime("%Y-%m"))
        months = set(mon)
        d = []
        v = []
        for x in months:
            n = (df_monthly.loc[x, 'Sum'].prod() - 1) * 100
            d.append(x)
            v.append(n)
        com_frame = pd.DataFrame(index=d, data=v)
        com_frame = com_frame.sort_index()
        com_frame.index = com_frame.index.map(str)
        # com_frame.index = pd.to_datetime(com_frame.index)
        df_montly = com_frame
        df_montly.columns = ["Result"]

        # ----------------------------------------------------------------------- #
        # Create figures in Express
        progress(20)

        df_accum_fig1 = df.astype(float)
        df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
        df_accum_fig1 = df_accum_fig1.round(2)
        fig1 = px.line(df_accum_fig1,
                       x=df_accum_fig1.index,
                       y=df_accum_fig1["Accumulation"],
                       hover_data=df_accum_fig1.columns[:-2])  # show all columns values excluding last 2

        df_montly_fig3 = df_montly.astype(float)
        color = []
        for i in df_montly_fig3["Result"]:
            if i < 0:
                color.append('red')
            else:
                color.append('green')
        df_montly_fig3["color"] = color
        df_montly_fig3 = df_montly_fig3.round(2)
        fig2 = px.bar(df_montly_fig3,
                      x=df_montly_fig3.index,
                      y=df_montly_fig3["Result"],
                      color=df_montly_fig3["color"],
                      color_discrete_sequence=df_montly_fig3["color"].unique())

        df_drawdown_fig2 = df_drawdown.astype(float)
        df_drawdown_fig2.iloc[:, :-2] = (df_drawdown_fig2.iloc[:, :-2] * 100)
        df_drawdown_fig2 = df_drawdown_fig2.round(2)
        fig3 = px.line(df_drawdown_fig2,
                       x=df_drawdown_fig2.index,
                       y=df_drawdown_fig2["Sum"] * 100,
                       hover_data=df_drawdown_fig2.columns[:-2])  # show all columns values excluding last 2


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
        this_figure = sp.make_subplots(rows=3, cols=1,
                                       vertical_spacing=0.1,
                                       shared_xaxes=True,
                                       subplot_titles=("Puzzle accumulative return",
                                                       "Puzzle monthly return",
                                                       "Puzzle Drawdown"))

        for traces in figure1_traces:
            this_figure.append_trace(traces, row=1, col=1)

        for traces in figure2_traces:
            this_figure.append_trace(traces, row=2, col=1)

        for traces in figure3_traces:
            this_figure.append_trace(traces, row=3, col=1)

        this_figure.update_layout(hovermode='x', showlegend=False)
        # Prefix y-axis tick labels with % sign
        this_figure.update_yaxes(tickprefix="%")
        this_figure['layout'].update(height=1400, title='Puzzle plotting results')

        progress(20)
        end_progress()

        # ----------------------------------------------------------------------- #
        # Printing stats

        print(frame)

        # ----------------------------------------------------------------------- #
        # Printing plots

        this_figure.show()


if __name__ == "__main__":
    backtest
