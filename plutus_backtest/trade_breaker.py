import pandas as pd
import yfinance as yf

def _sl_tp(stop_loss_dic, take_profit_dic):
    com_dic = {**stop_loss_dic, **take_profit_dic}
    if bool(com_dic):
        sltp_df = pd.DataFrame(com_dic).T
        sltp_df.columns = ['Date', 'Level', 'Type']
        exit_price = []
        for x in sltp_df.index:
            exit_price.append(str(round(float(yf.download(x,sltp_df.loc[x,'Date'],sltp_df.loc[x,'Date'],  progress=False)['Adj Close'].values),3)))
        sltp_df['Exit price'] = exit_price.copy()
        sltp_df['Date'] = sltp_df['Date'].astype(str)
        return sltp_df
    else:
        print('Portfolio assets havent reached stop_loss/take_profit levels')