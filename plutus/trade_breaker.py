import warnings
warnings.simplefilter(action='ignore', category=Warning)

import pandas as pd

def _sl_tp(stop_loss_dic, take_profit_dic,prices):
    com_dic = {**stop_loss_dic, **take_profit_dic}
    if bool(com_dic):
        sltp_df = pd.DataFrame(com_dic).T
        sltp_df.columns = ['Date', 'Level', 'Type']
        exit_price = []
        for x in sltp_df.index:
            data= round(prices[prices['ticker']==x].loc[sltp_df.loc[x,'Date']].values[1],2)
            exit_price.append(data)
        sltp_df['Exit price'] = exit_price.copy()
        sltp_df['Date'] = sltp_df['Date'].astype(str)
        st = []
        for x in range(len(sltp_df.index)):
            st.append(sltp_df['Date'].values[x][8:10] + '-' + sltp_df['Date'].values[x][5:7] +
                      '-' + sltp_df['Date'].values[x][2:4])
        sltp_df['Date'] = st
        sltp_df.reset_index(inplace=True)
        sltp_df.rename(columns={'index': 'Asset'}, inplace = True)
        return sltp_df
    else:
        empty_df = pd.DataFrame({0: ["None amongst provided assets has reached sl/tp levels"]}).T
        empty_df.rename(columns={0:"SL/TP info"}, inplace =True)
        return empty_df