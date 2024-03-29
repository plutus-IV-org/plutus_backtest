import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

def _plot_formatting(fig):
    font = "system-ui"
    fig.update_layout(font_family=font,
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       title_font_size=20, title_x=0.1, showlegend=False, font_color='rgb(255, 255, 255)',
                       xaxis=dict(
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='rgb(0, 0, 0)',
                           linewidth=2,
                           ticks='outside',
                           tickfont=dict(
                               family=font,
                               size=12,
                               color='rgb(255, 255, 255)',
                           )),
                       yaxis=dict(
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='rgb(255, 255, 255)',
                           linewidth=2,
                           ticks='outside',
                           tickfont=dict(
                               family=font,
                               size=12,
                               color='rgb(255, 255, 255)',
                           )), )
    return fig

def _plot_formatting_short(fig):
    font = "system-ui"
    fig.update_layout(font_family=font,
                       paper_bgcolor='rgba(0,0,0,0)',
                       plot_bgcolor='rgba(0,0,0,0)',
                       title_font_size=28, title_x=0.1, showlegend=False, font_color='rgb(0, 0, 0)',
                       font=dict(
                           family=font,
                           size=20,
                           color='rgb(0, 0, 0)',
                       ),
                       xaxis=dict(
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='rgb(0, 0, 0)',
                           linewidth=2,
                           ticks='outside',
                           tickfont=dict(
                               family=font,
                               size=18,
                               color='rgb(0, 0, 0)',
                           )),
                       yaxis=dict(
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='rgb(0, 0, 0)',
                           linewidth=2,
                           ticks='outside',
                           tickfont=dict(
                               family=font,
                               size=18,
                               color='rgb(0, 0, 0)',
                           )), )
    return fig

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Accumulated return with normal formatting for full report
def _accumulated_return(final_portfolio, benchmark_performance, benchmark_ticker = None):

    accumulated_return = final_portfolio.copy()
    d1 = accumulated_return[['Accumulation']]

    avg = 0
    dis_b = avg - d1.min()
    m1 = (d1.min() + (dis_b/4)).values
    m2 = (d1.min() + (dis_b/2)).values
    m3 = (d1.min() + (dis_b*0.75)).values
    dis_t = d1.max()- avg
    b1 = (avg + (dis_t/4)).values
    b2 = (avg +(dis_t/2)).values
    b3 = (avg + (dis_t * 0.75)).values
    labels = []
    for x in d1.Accumulation.values:
        if x < m1:
            labels.append(1)
        elif x< m2 and x>m1:
            labels.append(2)
        elif x<m3 and x>m2:
            labels.append(3)
        elif x<avg and x>m3:
            labels.append(4)
        elif x<b1 and x> avg:
            labels.append(5)
        elif x<b2 and x>b1:
            labels.append(6)
        elif x<b3 and x>b2:
            labels.append(7)
        else:
            labels.append(8)
    d1 = d1.copy()
    d1['quantiles'] = labels

    c1 = 'RGB(215, 48, 39)'
    c2 = 'RGB(244, 109, 67)'
    c3 = 'RGB(253, 174, 97)'
    c4 = 'RGB(254, 224, 139)'
    c5 = 'RGB(217, 239, 139)'
    c6 = 'RGB(166, 217, 106)'
    c7 = 'RGB(102, 189, 99)'
    c8 = 'RGB(26, 152, 80)'
    lst = []
    for y in d1['quantiles']:
        if y==1:
            lst.append(c1)
        elif y==2:
            lst.append(c2)
        elif y==3:
            lst.append(c3)
        elif y==4:
            lst.append(c4)
        elif y==5:
            lst.append(c5)
        elif y==6:
            lst.append(c6)
        elif y==7:
            lst.append(c7)
        else:
            lst.append(c8)
    d1['Palette'] = lst

    fig = px.scatter(d1, x=d1.index, y=d1["Accumulation"], title="Accumulated return",
                      color=d1["Accumulation"], color_continuous_scale='RdYlGn',
                      labels={'index': "Time", 'Accumulation': 'Return %'},
                       range_x=[d1.index[0], d1.index[-1] + timedelta(2)])

    fig = _plot_formatting(fig)

    for x in range(len(d1.index)):
        sdf = d1.iloc[x: x + 2]
        col = sdf.Palette.values[-1]
        fig.add_trace(go.Scatter(x=sdf.index, y=sdf['Accumulation'],
                                  line=dict(color=col, width=7),hovertemplate= '<b><i>Portfolio return</i></b>: <i>%{y:.2f}%<i>,<br><b>Date</b>: %{x}<br><extra></extra>'))

    if benchmark_ticker is not None:
        benchmark_performance.loc[benchmark_performance.index[0]-timedelta(1)] = 1
        benchmark_performance.sort_index(inplace = True)
        fig.add_trace(go.Scatter(x=benchmark_performance.index,
                         y=benchmark_performance["Bench_Accumulation"], name="Benchmark",
                         line=dict(color= 'rgb(141, 140, 141)', width=3, dash='dashdot'), hovertemplate= '<b><i>Benchmark return</i></b>: <i>%{y:.2f}%<i>,<br><b>Date</b>: %{x}<br><extra></extra>'))
    fig.update_layout(hovermode="closest", showlegend= False)

    return fig

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Accumulated return with adjusted formatting for short report
def _accumulated_return_short(final_portfolio, benchmark_performance, benchmark_ticker = None):

    accumulated_return = final_portfolio.copy()
    d1 = accumulated_return[['Accumulation']].copy()

    avg = 0
    dis_b = avg - d1.min()
    m1 = (d1.min() + (dis_b/4)).values
    m2 = (d1.min() + (dis_b/2)).values
    m3 = (d1.min() + (dis_b*0.75)).values
    dis_t = d1.max()- avg
    b1 = (avg + (dis_t/4)).values
    b2 = (avg +(dis_t/2)).values
    b3 = (avg + (dis_t * 0.75)).values
    labels = []
    for x in d1.Accumulation.values:
        if x < m1:
            labels.append(1)
        elif x< m2 and x>m1:
            labels.append(2)
        elif x<m3 and x>m2:
            labels.append(3)
        elif x<avg and x>m3:
            labels.append(4)
        elif x<b1 and x> avg:
            labels.append(5)
        elif x<b2 and x>b1:
            labels.append(6)
        elif x<b3 and x>b2:
            labels.append(7)
        else:
            labels.append(8)
    d1['quantiles'] = labels

    c1 = 'RGB(215, 48, 39)'
    c2 = 'RGB(244, 109, 67)'
    c3 = 'RGB(253, 174, 97)'
    c4 = 'RGB(254, 224, 139)'
    c5 = 'RGB(217, 239, 139)'
    c6 = 'RGB(166, 217, 106)'
    c7 = 'RGB(102, 189, 99)'
    c8 = 'RGB(26, 152, 80)'
    lst = []
    for y in d1['quantiles']:
        if y==1:
            lst.append(c1)
        elif y==2:
            lst.append(c2)
        elif y==3:
            lst.append(c3)
        elif y==4:
            lst.append(c4)
        elif y==5:
            lst.append(c5)
        elif y==6:
            lst.append(c6)
        elif y==7:
            lst.append(c7)
        else:
            lst.append(c8)
    d1['Palette'] = lst.copy()

    fig = px.scatter(d1, x=d1.index, y=d1["Accumulation"], title="Accumulated return",
                      color=d1["Accumulation"], color_continuous_scale='RdYlGn',
                      labels={'index': "Time", 'Accumulation': 'Return %'},
                       range_x=[d1.index[0], d1.index[-1] + timedelta(2)])

    fig = _plot_formatting_short(fig)

    for x in range(len(d1.index)):
        sdf = d1.iloc[x: x + 2]
        col = sdf.Palette.values[-1]
        fig.add_trace(go.Scatter(x=sdf.index, y=sdf['Accumulation'],
                                  line=dict(color=col, width=7),hovertemplate= '<b><i>Portfolio return</i></b>: <i>%{y:.2f}%<i>,<br><b>Date</b>: %{x}<br><extra></extra>'))

    if benchmark_ticker is not None:
        benchmark_performance.loc[benchmark_performance.index[0]-timedelta(1)] = 1
        benchmark_performance.sort_index(inplace = True)
        fig.add_trace(go.Scatter(x=benchmark_performance.index,
                         y=benchmark_performance["Bench_Accumulation"], name="Benchmark",
                         line=dict(color= 'rgb(141, 140, 141)', width=3, dash='dashdot'), hovertemplate= '<b><i>Benchmark return</i></b>: <i>%{y:.2f}%<i>,<br><b>Date</b>: %{x}<br><extra></extra>'))
    fig.update_layout(hovermode="closest", showlegend= False)

    return fig

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Drawdown
def _drawdown(final_portfolio):
    port_performance_drawdown = final_portfolio.copy()
    port_performance_drawdown = port_performance_drawdown.clip(upper=0)
    port_performance_drawdown = port_performance_drawdown.drop(columns=['Sum', 'Accumulation'])
    # port_performance_drawdown = abs(port_performance_drawdown)
    port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
    port_performance_drawdown['Accumulation'] = (port_performance_drawdown['Sum'].cumsum()) * 100
    df_drawdown = port_performance_drawdown.copy()
    df_drawdown = df_drawdown.round(decimals=3)

    df_drawdown_fig2 = df_drawdown.astype(float)
    df_drawdown_fig2.iloc[:, :-2] = (df_drawdown_fig2.iloc[:, :-2] * 100)
    df_drawdown_fig2 = df_drawdown_fig2.round(2)
    dff = df_drawdown_fig2[df_drawdown_fig2.columns[:-2]].copy()
    dff['Rounded total'] = df_drawdown_fig2["Sum"] * 100
    dff.index.name = 'Date'
    fig = px.line(dff,
                   x=dff.index,
                   y='Rounded total',
                   hover_data=dff.columns[:-1],
                   title="Drawdown")
    fig.update_traces(line_color='red')
    fig = _plot_formatting(fig)

    fig.update_traces(line_color='red')

    fig.update_layout(xaxis_title="Time",
                      yaxis_title="Return")

    return fig
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Monthly return
def _monthly_return(final_portfolio):
    mon = []
    df_monthly = final_portfolio.copy()
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
    df_montly.columns = ["Return"]

    df_montly_fig3 = df_montly.astype(float)
    color = []
    for i in df_montly_fig3["Return"]:
        if i < 0:
            color.append('red')
        else:
            color.append('green')
    df_montly_fig3["color"] = color
    df_montly_fig3 = df_montly_fig3.round(2)
    df_montly_fig3.index.name = 'Date'
    fig = px.bar(df_montly_fig3,
                  x=df_montly_fig3.index,
                  y=df_montly_fig3["Return"],
                  color=df_montly_fig3["color"],
                  color_discrete_sequence=df_montly_fig3["color"].unique(),
                  title="Monthly return")
    fig.update_traces(hovertemplate='<b><i>Return</i></b>: <i>%{y:.2f}%<i>,<br><b>Month</b>: %{x|%b %Y}<br><extra></extra>')
    fig = _plot_formatting(fig)

    fig.update_layout(xaxis_title="Time",
                      yaxis_title="Return")

    return fig
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Gantt
def _gantt (security_list):
    gantt = px.timeline(security_list, x_start="start day", x_end="end day", y="company") #additional Gantt graph
    gantt.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    gantt['layout'].update(height=1500, title='Plotting results')

    return gantt

def _weights_distribution (portfolio_weights, major_assets):
    """
    Weights rebalancing graph serves only to visualize the percentage of the capital being invested in  the moment of
    weights rebalancing. The total sum of the weights is always 100% since during rebalance the assets are getting the
    weights according to the weights factor provided and total capital at that moment.
    """
    weights_df = portfolio_weights.copy()
    if len(major_assets) != len(portfolio_weights.columns):
        ma = major_assets.copy()
        rest = weights_df.drop(columns=ma, axis=1).sum(axis=1).values
        major = weights_df[ma]
        major['Minors'] = rest
        weights_df = major.copy()
        weights_df["Total Weights"] = abs(weights_df).sum(axis=1)
        weights_df = weights_df[weights_df["Total Weights"] != 0]
        weights_df = weights_df.drop("Total Weights", axis=1)
        weights_df = abs(weights_df)
    else:
        weights_df["Total Weights"] = abs(weights_df).sum(axis=1)
        weights_df = weights_df[weights_df["Total Weights"] != 0]
        weights_df = weights_df.drop("Total Weights", axis=1)
        weights_df = abs(weights_df)
    fig = px.area(weights_df * 100,
                   x=weights_df.index,
                   y=weights_df.columns,hover_data= weights_df.columns.name,
                   title="Weights rebalancing")

    fig = _plot_formatting(fig)

    fig.update_layout(xaxis_title="Time",
                      yaxis_title="Weights percentage", showlegend=False, hovermode="x")
    names = {'variable': '<b><i>Asset</b></i>', 'index' : '<b><i>Date</b></i>', 'value': '<b><i>Weights</b></i>'}
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('variable', names['variable'])))
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('index', names['index'])))
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('value', names['value'])))

    return fig

def _capitlised_weights_distribution(capitlised_weights_distribution, major_assets):
    """
    Weights change graph is oriented to represent how the return is being distributed among the traded assets  as well
    as providing the information how the capital would be split between the assets over the time compare to the initial
    trade date. It allows visualization understanding which asset is generating positive return and which one is actually
    generating the loss. An increase of asset area states the overall percentage of the capital is invested in this asset.
    """

    df = capitlised_weights_distribution.drop(columns= 'Accu')
    for x in df.index:
        if df.loc[x].sum() ==0:
            df.drop(index=x, inplace=True)
    if len(major_assets)!= len(df.columns):
        ma = major_assets.copy()
        rest = df.drop(columns=ma, axis=1).sum(axis=1).values
        major = df[ma]
        major['Minors'] = rest
        df = major.copy()
    fig = px.area(df,
                   x=df.index,
                   y=df.columns,
                   title="Weights change")

    fig = _plot_formatting(fig)

    fig.update_layout(xaxis_title="Time",
                      yaxis_title="Weights percentage", showlegend=False, hovermode="x")
    names = {'variable': '<b><i>Asset</b></i>', 'index' : '<b><i>Date</b></i>', 'value': '<b><i>Weights</b></i>'}
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('variable', names['variable'])))
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('index', names['index'])))
    fig.for_each_trace(lambda t: t.update(hovertemplate=t.hovertemplate.replace('value', names['value'])))
    return fig

def _bar_weights_changes(capitlised_weights_distribution, major_assets):
    df = capitlised_weights_distribution.drop(columns='Accu')
    for x in df.index:
        if df.loc[x].sum() == 0:
            df.drop(index=x, inplace=True)
    if len(major_assets) != len(df.columns):
        ma = major_assets.copy()
        rest = df.drop(columns=ma, axis=1).sum(axis=1).values
        major = df[ma]
        major['Minors'] = rest
        df = major.copy()
    ef = pd.DataFrame()
    tic = []
    for x in df.columns:
        a1 = df[x]
        tic.append([a1.name] * len(a1))
        ef = pd.concat([ef, a1])
        flat_list = [x for xs in tic for x in xs]
    ef[1] = flat_list
    ef.index = ef.index.strftime("%Y-%m-%d")
    ef.index.name = 'Date'
    ef.rename(columns={0: 'Weights', 1: 'Asset'}, inplace=True)
    fig = px.bar(ef, x='Asset', y='Weights', color='Weights', color_continuous_scale="RdYlGn",
                  pattern_shape="Asset", pattern_shape_sequence=["x"], animation_frame=ef.index,
                  range_y=[-1, 1], title="Weights change animated")
    fig.update_yaxes(showgrid=False)
    fig.update_layout(plot_bgcolor='rgb(255, 255, 255)')
    if len(ef) > 250:
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 250
    else:
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 500
    fig.update_layout(barmode='stack', bargap=0.01, hovermode="closest")
    fig.update_layout(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig = _plot_formatting(fig)
    return fig

def _bar_weights_rebalance(portfolio_weights, major_assets):
    weights_df = portfolio_weights.copy()
    if len(major_assets) != len(portfolio_weights.columns):
        ma = major_assets.copy()
        rest = weights_df.drop(columns=ma, axis=1).sum(axis=1).values
        major = weights_df[ma]
        major['Minors'] = rest
        weights_df = major.copy()
        weights_df["Total Weights"] = abs(weights_df).sum(axis=1)
        weights_df = weights_df[weights_df["Total Weights"] != 0]
        weights_df = weights_df.drop("Total Weights", axis=1)
        weights_df = abs(weights_df)
    else:
        weights_df["Total Weights"] = abs(weights_df).sum(axis=1)
        weights_df = weights_df[weights_df["Total Weights"] != 0]
        weights_df = weights_df.drop("Total Weights", axis=1)
        weights_df = abs(weights_df)
    ef = pd.DataFrame()
    tic = []
    for x in weights_df.columns:
        a1 = weights_df[x]
        tic.append([a1.name] * len(a1))
        ef = pd.concat([ef, a1])
        flat_list = [x for xs in tic for x in xs]
    ef[1] = flat_list
    ef.index = ef.index.strftime("%Y-%m-%d")
    ef.index.name = 'Date'
    ef.rename(columns={0: 'Weights', 1: 'Asset'}, inplace=True)
    fig = px.bar(ef, x='Asset', y='Weights', color='Weights', color_continuous_scale="RdYlGn",
                  pattern_shape="Asset", pattern_shape_sequence=["x"], animation_frame=ef.index,
                  range_y=[-1, 1], title="Weights rebalance animated")
    fig.update_yaxes(showgrid=False)
    fig.update_layout(plot_bgcolor='rgb(255, 255, 255)')
    if len(ef)>250:
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 250
    else:
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 500
    fig.update_layout(barmode='stack', bargap=0.01, hovermode="closest")
    fig.update_layout(showlegend=False)
    fig.update(layout_coloraxis_showscale=False)
    fig = _plot_formatting(fig)
    return fig


