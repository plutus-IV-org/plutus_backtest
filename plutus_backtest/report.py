import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from tabulate import tabulate
from datetime import timedelta
pd.options.mode.chained_assignment = None
from plutus_backtest.backtest import _security_list, _consolidated_table_detailed, _portfolio_construction, _stats
from plutus_backtest.plots import _accumulated_return, _monthly_return, _drawdown, _plotting
from plutus_backtest.benchmark import _benchmark_construction
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, dcc, dash_table
import visdcc

def execution(asset, o_day, c_day, weights_factor=None,
                       take_profit=None,
                       stop_loss=None,
                       benchmark=None,
                       price_period_relation=None):
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Structuring input

    weights_factor = weights_factor if weights_factor is not None else np.ones(len(asset))
    take_profit = take_profit if take_profit is not None else len(asset) * [np.inf]
    stop_loss = stop_loss if stop_loss is not None else len(asset) * [-np.inf]

    if price_period_relation is None:
        p_p_p = "Open"
        p_p_n = "Adj Close"
    else:
        if price_period_relation == 'O-C':
            p_p_p = "Open"
            p_p_n = "Adj Close"
        elif price_period_relation == 'C-O':
            p_p_p = "Adj Close"
            p_p_n = "Open"
        elif price_period_relation == 'C-C':
            p_p_p = "Adj Close"
            p_p_n = "Adj Close"
        else:
            p_p_p = "Open"
            p_p_n = "Open"

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _security_list

    security_list = _security_list(asset=asset,
                                   o_day=o_day,
                                   c_day=c_day,
                                   weights_factor=weights_factor,
                                   take_profit=take_profit,
                                   stop_loss=stop_loss)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _benchmark_construction
    if benchmark == None:
        benchmark_construction = None
    else:
        benchmark_construction = _benchmark_construction(security_list = security_list,
                                                         benchmark = benchmark,
                                                         p_p_n = p_p_n,
                                                         p_p_p = p_p_p)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _consolidated_table_detailed

    consolidated_table_detailed, auxiliar_df, security_list, weights_factor = _consolidated_table_detailed(security_list = security_list,
                                                                                           asset = asset,
                                                                                           o_day=o_day,
                                                                                           c_day=c_day,
                                                                                           weights_factor=weights_factor,
                                                                                           take_profit=take_profit,
                                                                                           stop_loss=stop_loss,
                                                                                           p_p_n = p_p_n,
                                                                                           p_p_p = p_p_p)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _portfolio_construction
    final_portfolio, portfolio_weights, capitlised_weights_distribution = _portfolio_construction(detailed_return = consolidated_table_detailed,
                                                     security_list = security_list,
                                                     auxiliar_df = auxiliar_df,
                                                     weights_factor=weights_factor)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _stats
    stats = _stats(final_portfolio)
    print(tabulate(stats.set_index('Indicators'), headers='keys', tablefmt='fancy_grid'))

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Plotting
    accumulated_return = _accumulated_return(final_portfolio=final_portfolio)
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
    d1['quantiles'] =labels
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

    fig1 = px.scatter(d1, x=d1.index, y=d1["Accumulation"], title="Accumulated return",
                      color=d1["Accumulation"], color_continuous_scale='RdYlGn',
                      labels={'index': "Time", 'Accumulation': 'Return'},
                       range_x=[d1.index[0], d1.index[-1] + timedelta(2)])

    fig1.update_layout(font_family="Bahnschrift Condensed",
                       plot_bgcolor='rgb(250, 250, 245)',
                       title_font_size=20, title_x=0, showlegend=False, font_color='Black',
                       xaxis=dict(
                           showline=True,
                           showgrid=False,
                           showticklabels=True,
                           linecolor='rgb(0, 0, 0)',
                           linewidth=2,
                           ticks='outside',
                           tickfont=dict(
                               family='Bahnschrift Condensed',
                               size=12,
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
                               family='Bahnschrift Condensed',
                               size=12,
                               color='rgb(0, 0, 0)',
                           )), )

    for x in range(len(d1.index)):
        sdf = d1.iloc[x: x + 2]
        col = sdf.Palette.values[-1]
        fig1.add_trace(go.Scatter(x=sdf.index, y=sdf['Accumulation'],
                                  line=dict(color=col, width=7)))

    fig1.show()
    monthly_return = _monthly_return(final_portfolio=final_portfolio)
    drawdown = _drawdown(final_portfolio=final_portfolio)
    plots = _plotting(accumulated_return=accumulated_return,
                                                          monthly_return=monthly_return,
                                                          drawdown=drawdown,
                                                          portfolio_weights=portfolio_weights,
                                                          capitlised_weights_distribution=capitlised_weights_distribution,
                                                          benchmark_performance=benchmark_construction,
                                                          benchmark_ticker=benchmark)


    gantt = px.timeline(security_list, x_start="start day", x_end="end day", y="company") #additional Gantt graph
    gantt.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up
    gantt['layout'].update(height=1500, title='Plotting results')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Building app

    security_list_short = security_list.head(10)

    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

    sidebar = dbc.Card(
        [
            html.Div(
                [
                    dash_table.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        data = stats.to_dict('records'),
                        columns = [{"name": i, "id": i} for i in stats.columns]
                    )
                ]
            ),
            html.Hr(),
            html.Div(
                [
                    dash_table.DataTable(
                        style_data={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                        },
                        data = security_list_short.to_dict('records'),
                        columns = [{"name": i, "id": i} for i in security_list_short.columns]
                    )
                ]
            )
        ]
    )

    main_graphs = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=plots)
                ]
            )
        ]
    )


    security_list_table = dbc.Card(
        [
            html.Div(
                [
                    dash_table.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        data=security_list.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in security_list.columns]
                    )
                ]
            ),

        ]
    )

    gantt_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=gantt)
                ]
            )
        ]
    )

    button = dbc.Card(
        [
            html.Div(
                [
                    html.Button("Download", id="click1"),
                    visdcc.Run_js(id="javascript")
                ]
            )
        ]
    )


    tab1_content = dbc.Container(
        [
            html.H1("Backtest results"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(sidebar, md=4),
                    dbc.Col(main_graphs),
                ],
                align="top",
            ),
            dbc.Row(
                [
                    dbc.Col(button),
                ],
                align="left",
            ),
        ],
        fluid=True,
    )


    tab2_content = dbc.Container(
        [
            html.H1("Gantt graph and full list of assets"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(security_list_table, md=4),
                    dbc.Col(gantt_graph),
                ],
                align="top",
            ),
            dbc.Row(
                [
                    #dbc.Col(button),
                ],
                align="left",
            ),
        ],
        fluid=True,
    )


    tabs = dbc.Tabs(
        [
            dbc.Tab(tab1_content, label="Backtest results"),
            dbc.Tab(tab2_content, label="Full assets list"),
        ]
    )

    app.layout = tabs

    app.title = "Plutus Backtest App!"


    @app.callback(
        Output("javascript", "run"),
        [Input("click1", "n_clicks")])
    def myfun(x):
        if x:
            return "window.print()"
            return ""

    app.run_server(debug=True, port=8888)
