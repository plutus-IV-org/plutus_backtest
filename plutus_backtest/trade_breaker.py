import pandas as pd
import yfinance as yf

def _sl_tp(stop_loss_dic, take_profit_dic):
    com_dic = {**stop_loss_dic, **take_profit_dic}
    if bool(com_dic):
        sltp_df = pd.DataFrame(com_dic).T
        sltp_df.columns = ['Date', 'Level', 'Type']
        exit_price = []
        return sltp_df

    else:
        print('Portfolio assets havent reached stop_loss/take_profit levels')