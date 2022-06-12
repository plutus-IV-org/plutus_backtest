import pandas as pd
import yfinance as yf

def _sl_tp(stop_loss_dic, take_profit_dic,prices):
    com_dic = {**stop_loss_dic, **take_profit_dic}
    if bool(com_dic):
        sltp_df = pd.DataFrame(com_dic).T
        sltp_df.columns = ['Date', 'Level', 'Type']
        exit_price = []
        for x in sltp_df.index:
            data= round(prices[prices['ticker']==x].loc[sltp_df.loc[x,'Date']].values[1],2)
            exit_price.append(str(data))
        sltp_df['Exit price'] = exit_price.copy()
        sltp_df['Date'] = sltp_df['Date'].astype(str)
        sltp_df.reset_index(inplace=True)
        sltp_df = sltp_df.rename(columns={'index': 'Company'})
        return sltp_df
    else:
        empty_df = pd.DataFrame({0: ["None amongst provided assets has reached sl/tp levels"]}).T.set_index(0)
        return empty_df