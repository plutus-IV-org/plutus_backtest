import pandas as pd
import yfinance as yf
import numpy as np
from plutus_backtest.backtest import _date_plus_one


def _benchmark_construction(security_list, benchmark, p_p_n, p_p_p):

    min_date = min(security_list['start day'])
    max_date = max(security_list['end day'])
    df = yf.download(benchmark, start=_date_plus_one(min_date),
                     end=_date_plus_one(max_date), progress=False)
    df['Ticker'] = benchmark
    df_close = df[["Ticker", p_p_n]]
    df_close.columns = ['ticker', 'close_price']
    df_open = df[["Ticker", p_p_p]]
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
    benchmark_performance = performance

    return benchmark_performance