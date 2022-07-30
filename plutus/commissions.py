import pandas as pd
import numpy as np
import datetime as dt
def commission(final_portfolio, special_assets, work_days, only_working_days,
               non_working_days_rebalance,broker_commission, weights_df):
    #1 only weekdays
    final_port = final_portfolio.copy()
    wdf = weights_df.copy()
    if only_working_days == True:
        for x in final_port.columns:
            final_port.loc[final_port[x].replace(0, np.nan).first_valid_index(), x] = \
                final_port.loc[final_port[x].replace(0, np.nan).first_valid_index(), x] - broker_commission
            if x in special_assets:
                px = final_port[x].replace(0, np.nan).dropna()
                for y in range(len(px.index) - 1):
                    if px.index[y + 1] - dt.timedelta(1) != px.index[y]:
                        final_port.loc[px.index[y + 1], x] = final_port.loc[px.index[y + 1], x] - broker_commission
        return final_port
    #2 all days
    if only_working_days == False:
        for i in wdf.columns:
            final_port.loc[final_port[i].replace(0, np.nan).first_valid_index(), i] = \
                final_port.loc[final_port[i].replace(0, np.nan).first_valid_index(), i] - broker_commission
            col = wdf[i]
            for q in range(len(wdf.index) - 1):
                if col.iloc[q + 1] != col.iloc[q] and col.iloc[q + 1] != 0:
                    final_port[i].iloc[q + 1] = final_port[i].iloc[q + 1] - broker_commission
        return final_port

        return final_port