import pandas as pd
import yfinance as yf
import numpy as np
from datetime import timedelta, datetime
import re


def _date_plus_one(d):
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

def _security_list(asset, o_day, c_day, weights_factor, take_profit, stop_loss):

    """
    :return:
        DataFrame with all input data.
    """

    if isinstance(asset, pd.core.series.Series):
        asset = asset.values
    if isinstance(weights_factor, pd.core.series.Series):
        weights_factor = weights_factor.values
    if isinstance(o_day, pd.core.series.Series):
        o_day = o_day.values
    if isinstance(c_day, pd.core.series.Series):
        c_day = c_day.values
    if isinstance(asset, pd.core.series.Series):
        asset = asset.values
    if isinstance(take_profit, pd.core.series.Series):
        take_profit = take_profit.values
    if isinstance(stop_loss, pd.core.series.Series):
        stop_loss = stop_loss.values
    if isinstance(o_day, np.ndarray):
        ls = []
        for x in range(len(o_day)):
            ls.append(str(o_day[x])[:10])
        o_day = ls
    if isinstance(c_day, np.ndarray):
        ls = []
        for x in range(len(c_day)):
            ls.append(str(c_day[x])[:10])
        c_day = ls
    df = pd.DataFrame(
        {"company": asset, "start day": o_day, "end day": c_day, "weights factor": weights_factor,
         "take profit": take_profit, "stop loss": stop_loss})
    df = df.set_index(df['company'])
    for x in range(len(df.index)):
        if df.iloc[x, 3] < 0 and df.iloc[x, 4] != np.inf and df.iloc[x, 5] != -np.inf:
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
    df = df.replace(-100500, -np.inf)

    security_list = df
    return security_list

def _consolidated_table_detailed(security_list, asset,
                                 o_day, c_day, weights_factor,
                                 take_profit, stop_loss, p_p_n, p_p_p):

    if isinstance(weights_factor, pd.core.series.Series):
        weights_factor = weights_factor.values

    # check if companies are dublicatted in a list
    df_original = security_list
    fq = pd.DataFrame(index=asset, data=o_day)
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

    #load prices from yahoo
    min_date = min(security_list['start day'])
    max_date = max(security_list['end day'])
    data = asset.copy()
    if type(data)!=list:
        data = list(data.values)
    ydata = yf.download(data, start=_date_plus_one(min_date),
                        end=_date_plus_one(max_date), progress=False)

    if ydata.empty:
        raise ValueError('No trading days were provided, perhaps days off or holidays have been given or non existing tickers')

    initial_df = pd.DataFrame()

    #check if column names are Multiindex
    if not isinstance(ydata.columns, pd.MultiIndex):
    #select desired start / end dates for selected companies
        for b_d, s_d, new_com in zip(df_original["start day"], df_original["end day"], list_new):
            data = ydata.loc[b_d:s_d].copy()
            data['Ticker'] = new_com
            initial_df = pd.concat([initial_df, data])
    else:
        for com, b_d, s_d, new_com in zip(df_original["company"], pd.to_datetime(df_original["start day"]),
                                          pd.to_datetime(df_original["end day"]), list_new):
            q1 = ydata.iloc[:, ydata.columns.get_level_values(1) == com]
            q1.columns = q1.columns.droplevel(1)
            data = q1.loc[b_d:s_d]
            data = data.copy()
            data['Ticker'] = new_com
            initial_df = pd.concat([initial_df, data])
    df_close = initial_df[["Ticker", p_p_n]]
    df_close.columns = ['ticker', 'close_price']
    df_open = initial_df[["Ticker", p_p_p]]
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
        merged_df = pd.concat([fake_df, get_end])
        merged_df['daily_change'] = merged_df['close_price'].pct_change()
        merged_df = merged_df.iloc[1:]
        aux_df = merged_df[['ticker', 'close_price']]
        work_df = merged_df[['ticker', 'daily_change']]
        em1 = pd.concat([em1, aux_df])
        em2 = pd.concat([em2, work_df])
    dc = em2.pivot_table(index=em2.index, columns='ticker', values='daily_change')

    asset = list_new

    # rerunning security_list again using dublicate adjusted tickers
    security_list = _security_list(asset=asset,
                                   o_day=o_day,
                                   c_day=c_day,
                                   weights_factor=weights_factor,
                                   take_profit=take_profit,
                                   stop_loss=stop_loss)

    if dc.columns.tolist() != asset:
        l1 = dc.columns.tolist()
        l2 = asset
        res = [x for x in l1 + l2 if x not in l1 or x not in l2]
        asset = l1
        security_list = security_list.drop(res)
        b_day = security_list['start day'].values
        s_day = security_list['end day'].values
        weights_factor = security_list['weights factor'].values
        sl = security_list['stop loss'].values
        tp = security_list['take profit'].values
        if res ==[]:
            pass
        else:
            print(f"\nNo price data found for {res} therefore was deleted from provided inputs.\n")

    dc = dc[security_list['company']]
    dc = dc.replace([np.inf, -np.inf], np.nan)
    dc = dc.fillna(0)
    dc = dc.apply(pd.to_numeric)
    aux = em1.pivot_table(index=em2.index, columns='ticker', values='close_price')
    aux = aux[security_list['company']]
    aux = aux.replace([np.inf, -np.inf], np.nan)
    aux = aux.fillna(0)
    aux = aux.apply(pd.to_numeric)
    auxiliar_df = aux.copy()
    detailed_return = dc.copy()

    return detailed_return, auxiliar_df, security_list, weights_factor, df_close

def _portfolio_construction(detailed_return, security_list, auxiliar_df, weights_factor, major_sample):
    """
    :return:
        Full constructed portfolio, including position length, weights factor, stop loss & take profit.
    """

    binary_weights = auxiliar_df / auxiliar_df
    binary_weights.fillna(value=0, inplace=True)
    fac_summing = np.sum(abs(np.array(weights_factor)))
    dist = np.array(weights_factor) / fac_summing
    dist_df = pd.DataFrame(index=security_list['company'], data=weights_factor).T
    weights_df = binary_weights * dist

    for z in weights_df.index:
        if abs(weights_df.loc[z]).sum() != 1:
            act = weights_df.loc[z][weights_df.loc[z] != 0]
            act_df = dist_df[act.index]
            new_dist = np.array(act_df) / np.sum(abs(np.array(act_df)))
            new_dist_frame = pd.DataFrame(columns=act.index, data=new_dist).T
            for i in new_dist_frame.index:
                weights_df.loc[z, i] = float(new_dist_frame.loc[i].values)
    accu = (detailed_return + 1).cumprod()
    dic_longs = {}
    dic_shorts = {}
    for x in accu.columns:
        q1 = accu[x]
        for y in q1:
            if y > security_list.loc[x, 'take profit'] and y!=0:
                q1.iloc[q1.values.tolist().index(y) + 1:] = 0
                if security_list.loc[x, 'weights factor'] > 0:
                    dic_longs[x] = accu.index[q1.values.tolist().index(y)], round(q1.iloc[q1.values.tolist().index(y)],3),'Take profit'
                else:
                    dic_shorts[x] = accu.index[q1.values.tolist().index(y)], round(q1.iloc[q1.values.tolist().index(y)],3), 'Stop loss'
            if y < security_list.loc[x, 'stop loss'] and y!=0:
                q1.iloc[q1.values.tolist().index(y) + 1:] = 0
                if security_list.loc[x, 'weights factor'] > 0:
                    dic_shorts[x] = accu.index[q1.values.tolist().index(y)], round(q1.iloc[q1.values.tolist().index(y)],3), 'Stop loss'
                else:
                    dic_longs[x] = accu.index[q1.values.tolist().index(y)], round(q1.iloc[q1.values.tolist().index(y)],3), 'Take profit'
    aux_table_2 = accu * binary_weights
    new_binary_weights = aux_table_2 / aux_table_2
    new_binary_weights.fillna(value=0, inplace=True)
    weights_df = new_binary_weights * dist

    stop_loss_assets = dic_shorts
    take_profit_assets = dic_longs

    for z in weights_df.index:
        if abs(weights_df.loc[z]).sum() != 1:
            act = weights_df.loc[z][weights_df.loc[z] != 0]
            act_df = dist_df[act.index]
            new_dist = np.array(act_df) / np.sum(abs(np.array(act_df)))
            new_dist_frame = pd.DataFrame(columns=act.index, data=new_dist).T
            for i in new_dist_frame.index:
                weights_df.loc[z, i] = float(new_dist_frame.loc[i].values)

    port_performance = weights_df * detailed_return
    port_performance['Sum'] = port_performance.sum(axis=1)
    port_performance['Sum'] = port_performance['Sum'] + 1
    port_performance['Accumulation'] = (port_performance['Sum'].cumprod() - 1) * 100

    #Weights changes
    #Creating table of rebalance of weights
    a1 = (abs(weights_df.diff()).sum(axis=1) != 0)
    a1.iloc[0] = True
    a1 = a1.astype(int)
    a2 = a1 * port_performance['Sum'].cumprod()
    a2.iloc[0] = 1
    a2 = a2.replace(to_replace=0, method='ffill')
    if a1.iloc[-1]==0:
        a1.iloc[-1]=1
    rebalance_days = a1[a1!=0].index
    # Adopting the weights to current return
    b1 = (a2.values * weights_df.T).T
    q1 = dist.copy()
    q1[q1>0]=1
    q1[q1<0]=-1
    detailed_return_orinted= detailed_return * q1
    ef = pd.DataFrame()
    # Calculating separated cumprod according to rebalncing days
    for x in range(len(rebalance_days)):
        if x!=len(rebalance_days)-1:
            m1 = (detailed_return_orinted.loc[rebalance_days[x]:rebalance_days[x +1]]+1).cumprod()
        else:
            m1 = (detailed_return_orinted.loc[rebalance_days[x]:]+1).cumprod()
        ef = pd.concat([ef,m1])
    ef = ef[~ef.index.duplicated(keep='first')]
    fff = ef* abs(b1)
    fff['Accumulation'] = port_performance['Accumulation'].values /100 +1
    #Clearing results due to diff price realtions
    df_deluted = (fff[fff.columns[:-1]].T * (fff['Accumulation']/ fff[fff.columns[:-1]].sum(axis=1)).replace(np.inf, 1).values).T
    df_deluted['Accu'] = port_performance['Accumulation'].values /100 +1
    capitlised_weights_distribution = df_deluted.copy()

    q1 = port_performance.index[0] - timedelta(days=1)  # starting from 0%
    port_performance.loc[q1] = [0] * len(port_performance.columns)
    port_performance = port_performance.sort_index()
    ##### Grouping indexies #####
    port_performance.columns = [re.sub('[0-9]', '', i) for i in port_performance.columns]
    final_portfolio = port_performance.T.groupby(level=[0], sort=False).sum().T

    weights_df.columns = [re.sub('[0-9]', '', i) for i in weights_df.columns]
    portfolio_weights = weights_df.T.groupby(level=[0], sort=False).sum().T

    capitlised_weights_distribution.columns = [re.sub('[0-9]', '', i) for i in capitlised_weights_distribution.columns]
    weights_changes = capitlised_weights_distribution.T.groupby(level=[0], sort=False).sum().T

    if major_sample == None:
        top_assets = portfolio_weights.columns.tolist()
    else:
        top_assets= abs(portfolio_weights).sum(axis=0).nlargest(major_sample).index.tolist()
    return final_portfolio, portfolio_weights, weights_changes, stop_loss_assets, take_profit_assets, top_assets

def _stats(final_portfolio):
    obj = final_portfolio
    pdr0 = obj['Sum']- 1
    pdr= pdr0.iloc[1:].copy()
    port_mean = pdr.mean()
    port_mean_pct = port_mean * 100
    port_std = pdr.std()
    LPM_0 = len(pdr[pdr < 0]) / len(pdr)
    LPM_1 = pdr.clip(upper=0).mean()
    LPM_2 = pdr.clip(upper=0).std()
    if LPM_0 == 0:
        LPM_0 = 0.01
    topless_pdr = pdr[pdr < port_std]
    botless_prd = topless_pdr[topless_pdr > -port_std]
    inner_mean = botless_prd.mean()
    obj_only_stocks = obj.drop(columns=['Sum', 'Accumulation'])
    stocks_mean = obj_only_stocks.mean()
    top_per = stocks_mean.nlargest(1)
    worst_per = stocks_mean.nsmallest(1)
    trade_length = len(pdr) - 1
    VaR_95 = -1.65 * port_std * np.sqrt(trade_length)
    VaR_99 = -2.33 * port_std * np.sqrt(trade_length)
    CVaR = LPM_1 / LPM_0
    list_1 = ['Mean', 'Std', 'Downside prob', 'Downside mean', 'Downside std', 'Investment period', 'VaR_95',
              'VaR_99', 'CVaR']
    list_2 = [port_mean, port_std, LPM_0, LPM_1, LPM_2, trade_length, VaR_95, VaR_99,
              CVaR]
    frame = pd.DataFrame({'Indicators': list_1, 'Values': list_2})
    #stat_frame = frame
    #frame = frame.to_string(index=False)

    return frame