import numpy as np
import pandas as pd
import plotly.express as px
from tabulate import tabulate
from plutus.calculations import _security_list, _consolidated_table_detailed, _portfolio_construction, _stats
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, dcc, dash_table
import visdcc


def _puzzle_preparation(asset, o_day, c_day, weights_factor=None,
                           take_profit=None,
                           stop_loss=None,
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
    # Calling _consolidated_table_detailed

    consolidated_table_detailed, auxiliar_df = _consolidated_table_detailed(security_list=security_list,
                                                                            asset=asset,
                                                                            o_day=o_day,
                                                                            p_p_n=p_p_n,
                                                                            p_p_p=p_p_p)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Calling _portfolio_construction
    final_portfolio, portfolio_weights = _portfolio_construction(detailed_return=consolidated_table_detailed,
                                                                 security_list=security_list,
                                                                 auxiliar_df=auxiliar_df,
                                                                 weights_factor=weights_factor)

    return final_portfolio, security_list





def _puzzle_assembly(data_dictionaries):
    """
    :param:
        dic: aggregated dictionary containing several constructed portfolios
    :return:
        Combines several backrests results into one dataframe
    """

    names = data_dictionaries.keys()
    empty_frame_data = pd.DataFrame()
    empty_frame_securities = pd.DataFrame()



    for x in names: #splitting tuple
        q1 = data_dictionaries[x][0][data_dictionaries[x][0].columns[:-2]] #performence results (first table in tuple)
        q2 = data_dictionaries[x][1] #securities lists (second table in tuple)

        empty_frame_data = pd.concat([empty_frame_data, q1])
        empty_frame_securities = pd.concat([empty_frame_securities, q2])

    df_sec = empty_frame_securities

    df_dic = empty_frame_data.sort_index(ascending=True)
    df_dic['Sum'] = (df_dic.sum(axis=1)) + 1
    df_dic['Accumulation'] = (df_dic['Sum'].cumprod() - 1) * 100
    df_dic = df_dic.fillna(0)
    df_dic = df_dic.astype(float)
    df_dic = df_dic.round(4)



    return df_dic, df_sec

def _puzzle_report_generator(performance_securities_tuple):
    """
    :param:
        data: aggregated dataframe from several backtests
    :return:
        Combined backtests statistic and cumulative return of the portfolio
    """



    df_data = performance_securities_tuple[0] #performance table as a first table from tuple
    df_sec = performance_securities_tuple[1] #second table from tuble (securyties list)

    df_data = df_data.round(decimals=3)
    df_data = df_data.fillna(0)
    q1 = df_data.iloc[:, :-2]
    q2 = sum(abs(q1).sum(axis=1) == 0)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Calling _stats

    stats = _stats(df_data)
    print(tabulate(stats, headers='keys', tablefmt='fancy_grid'))

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Plotting

    df_accum_fig1 = df_data.astype(float)
    df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
    df_accum_fig1 = df_accum_fig1.round(2)
    fig1 = px.line(df_accum_fig1,
                   x=df_accum_fig1.index,
                   y=df_accum_fig1["Accumulation"],
                   hover_data=df_accum_fig1.columns[:-2])  # show all columns values excluding last 2

    gantt = px.timeline(df_sec, x_start="start day", x_end="end day", y="company")
    gantt.update_yaxes(autorange="reversed")  # otherwise tasks are listed from the bottom up

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Building app

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
                        data=stats.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in stats.columns]
                    )
                ]
            )
        ]
    )

    line_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=fig1),
                ]
            )
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

    security_list_table = dbc.Card(
        [
            html.Div(
                [
                    dash_table.DataTable(
                        style_data={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        data=df_sec.to_dict('records'),
                        columns=[{"name": i, "id": i} for i in df_sec.columns]
                    )
                ]
            ),

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
                    dbc.Col(line_graph),
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
            html.H1("Gantt line_graph and full list of assets"),
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