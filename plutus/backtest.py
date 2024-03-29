import numpy as np
import pandas as pd
from tabulate import tabulate
from plutus.calculations import _security_list, _consolidated_table_detailed, _portfolio_construction, _stats
from plutus.plots import _accumulated_return, _accumulated_return_short, _weights_distribution, _capitlised_weights_distribution,\
    _monthly_return, _drawdown, _bar_weights_changes, _bar_weights_rebalance
from plutus.trade_breaker import _sl_tp
from plutus.benchmark import _benchmark_construction
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output
from jupyter_dash import JupyterDash
import re

def execution(asset, start, end, weights_factor=None,
                       take_profit=None,
                       stop_loss=None,
                       benchmark=None,
                       price_period_relation=None,
                       full_report = False,
                       major_sample = 10,
                       only_working_days= False,
                       non_working_days_rebalance =False,
                       broker_commission = 0
                        ):

    """ :Parameters:
               asset: str or list or series
                   Instruments taken into the consideration for the backtest.
               start: list of str or timestamps or series
                   Day/Days of the position opening.
               end: list of str or timestamps or series
                   Day/Days of the position closing.
               weights_factor: list of int or float or array-like or series default None
                   Optional list of factors which will be considered to define the weights for taken companies. By default
                   all weights are distributed equally, however if the list of factors provided the backtest will maximize
                   the weights towards the one with max weight factor. Negative weight factor will be considered as short selling.
               take_profit: list of float or int or series default None
                   List of values determining the level till a particular stock shall be traded.
               stop_loss: list of float or int or series default None
                   List of values determining the level till a particular stock shall be traded.
               benchmark: str default None
                   A benchmark ticker for comparison with portfolio performance
               price_period_relation: str default 'O-C'
                   Instruct what part of the trading day a position shall be opened,
                   and what part of trading day it shall be closed.
                   Possible relations:
                   O-C / Open to Close prices
                   C-O / Close to Open prices
                   C-C / Close to Close prices
                   O-O / Open to Open prices
                   "Open" - the price at which a security first trades upon the opening of an exchange on a trading day.
                   "Close" - value of the last transacted price in a security before the market officially closes.
               full_report: bool, optional, default False
                   Generates full report as PDF.
               major_sample: int or None, optional, default 10
                   Based on duration of the trading period as well as weights factor of the asset.
                   In order to make understandable visualisation in full report graphs such as weights changes and
                   weights distribution, major sample is used which will focus to provide info regarding main provided
                   assets. Can be changed to any int. If value is None the backtest will consider all assets as major
                   ones.
                only_working_days: bool, default False
                    Based on asset specification, the asset may be traded during the weekends or holidays, in order to
                    avoid such impact False parameter might be used.
                non_working_days_rebalance: bool, default False
                    If there are assets traded on weekends or holidays partial amount of portfolio weights is kept.
                    If the parameter is True the weights from non-traded assets will be rebalanced as per active assets
                    and its weights_factor.
                broker_commission: float, default 0
                    Setting brokerage commission per each trade.


    """



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
                                   start=start,
                                   end=end,
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

    consolidated_table_detailed, auxiliar_df, security_list, weights_factor, price_close, weekdays, special_assets= _consolidated_table_detailed(security_list = security_list,
                                                                                           asset = asset,
                                                                                           start=start,
                                                                                           end=end,
                                                                                           weights_factor=weights_factor,
                                                                                           take_profit=take_profit,
                                                                                           stop_loss=stop_loss,
                                                                                           p_p_n = p_p_n,
                                                                                           p_p_p = p_p_p,
                                                                                           only_working_days = only_working_days,
                                                                                           )

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _portfolio_construction
    final_portfolio, portfolio_weights, capitlised_weights_distribution, sl_dic, tp_dic, top_assets,times_commission_paid,commission_loss= _portfolio_construction(detailed_return = consolidated_table_detailed,
                                                    security_list = security_list,
                                                    auxiliar_df = auxiliar_df,
                                                    weights_factor=weights_factor,
                                                    major_sample = major_sample, weekdays= weekdays,
                                                    only_working_days= only_working_days,
                                                    non_working_days_rebalance= non_working_days_rebalance,
                                                    broker_commission= broker_commission,
                                                    special_assets = special_assets)
    final_portfolio.index.name = None
    portfolio_weights.index.name = None
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _sl_tp trade breaker
    if False in np.isinf(security_list[['take profit', 'stop loss']]).values:
        trade_breaker_frame = _sl_tp(sl_dic,tp_dic,price_close)
    else:
        trade_breaker_frame = pd.DataFrame()
        disable_button = True
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _stats
    stats = _stats(final_portfolio, times_commission_paid,commission_loss)
    stats = stats.round(4)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Plotting

    if full_report == False:
        print(tabulate(stats.set_index('Indicators'), headers='keys', tablefmt='fancy_grid'))
        plot = _accumulated_return_short(final_portfolio = final_portfolio,
                                   benchmark_performance = benchmark_construction,
                                   benchmark_ticker = benchmark).show()
        return plot, final_portfolio, portfolio_weights

    else:
        accumulated = _accumulated_return(final_portfolio = final_portfolio,
                                          benchmark_performance = benchmark_construction,
                                          benchmark_ticker = benchmark)
        monthly = _monthly_return(final_portfolio = final_portfolio)
        drawdown = _drawdown(final_portfolio = final_portfolio)
        weights_rebalance = _bar_weights_rebalance(portfolio_weights, top_assets)
        weights_changes = _bar_weights_changes(capitlised_weights_distribution,top_assets)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Building app
    security_list.rename(columns={'company': 'Top assets', 'start day': 'Start', 'end day': 'End', 'weights factor':'Weights factor',
                                  "take profit": "Take profit","stop loss":"Stop loss" }, inplace = True)
    lst = security_list.index
    lst = [re.sub('[0-9]', '', i) for i in lst]
    security_list.set_index([lst, lst], inplace = True)
    security_list['Top assets'] = lst.copy()
    security_list['Take profit'] = security_list['Take profit'].round(2)
    security_list['Stop loss'] = security_list['Stop loss'].round(2)
    security_list_short = security_list.loc[top_assets].head(10)
    st = []
    ed = []
    for x in range(len(security_list_short.index)):
        st.append(security_list_short['Start'].values[x][8:10]+'-' +security_list_short['Start'].values[x][5:7] +
                  '-' + security_list_short['Start'].values[x][2:4])
        ed.append(security_list_short['End'].values[x][8:10] + '-' + security_list_short['End'].values[x][5:7] +
                  '-' + security_list_short['End'].values[x][2:4])
    security_list_short['Start'] =st
    security_list_short['End'] = ed
    security_list_short.rename(columns = {'Start': 'Starting date', 'End':'  Ending  date  '}, inplace = True)

    app = JupyterDash(external_stylesheets=[dbc.themes.QUARTZ])

    if False in np.isinf(security_list[['Take profit', 'Stop loss']]).values:

        table_1 = dbc.Table.from_dataframe(security_list_short)
        table_2 = dbc.Table.from_dataframe(stats)
        table_3 = dbc.Table.from_dataframe(trade_breaker_frame)

        disable_button = False

        sidebar = dbc.Card(
            [
                html.Div(
                    [
                        table_2
                    ]
                ),
                html.Br(),
                html.Div(
                    [
                        table_1
                    ]
                ),
                html.Br(),
                html.Div(
                    [
                        table_3
                    ]
                ),
            ]
        )
    else:
        table_1 = dbc.Table.from_dataframe(security_list_short)
        table_2 = dbc.Table.from_dataframe(stats)

        disable_button = True

        sidebar = dbc.Card(
            [
                html.Div(
                    [
                        table_2
                    ]
                ),
                html.Br(),
                html.Div(
                    [
                        table_1
                    ]
                ),
            ]
        )

    main_graphs = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=accumulated),
                    dcc.Graph(id="cwd_graph_main"),
                    dcc.Graph(figure=monthly),
                    dcc.Graph(figure=drawdown),
                ]
            )
        ]
    )

    accumulation_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=accumulated)
                ]
            )
        ]
    )

    weights_graph = dbc.Card(
        [
            html.Div(
                [

                    dcc.Graph(id="weights_graph")
                ]
            )
        ]
    )

    cwd_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(id="cwd_graph_tab")
                ]
            )
        ]
    )

    montly_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=monthly)
                ]
            )
        ]
    )

    drawdown_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=drawdown)
                ]
            )
        ]
    )

    weights_changes_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=weights_changes)
                ]
            )
        ]
    )


    weights_rebalance_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=weights_rebalance)
                ]
            )
        ]
    )

    download_final_portfolio = dbc.Card(html.Div(
        [
        dbc.Button("Download final porfolio data", color="primary", id="btn_portfolio_csv",
                   style={"margin-bottom": "10px"}),
        dcc.Download(id="download-portfolio-csv"),
        ],className="d-grid gap-2"
    ))

    download_portfolio_weights = dbc.Card(html.Div(
        [
        dbc.Button("Download porfolio weights data", color="primary", id="btn_weights_csv",
                   style={"margin-bottom": "10px"}),
        dcc.Download(id="download-weights-csv"),
        ],className="d-grid gap-2"
    ))

    download_sl_tp_triggers = dbc.Card(html.Div(
        [
        dbc.Button("Download SL/TP triggers data", color="primary", id="btn_sl_tp_csv",
                   disabled=disable_button, style={"margin-bottom": "10px"}),
        dcc.Download(id="download-sl-tp-csv")
        ],className="d-grid gap-2"
    ))

    tab1_content = dbc.Container(
        [
            html.H1("Backtest results"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col([dbc.Row([sidebar,
                                    html.Hr(),      
                                      download_final_portfolio,
                                      html.Hr(),
                                      download_portfolio_weights,
                                      html.Hr(),
                                      download_sl_tp_triggers])], width=4),
                    dbc.Col(main_graphs, width=8),
                ],
                align="top",
            ),

        ],
        fluid=True,
    )


    tab2_content = dbc.Container(
        [
            html.H1("Accumulated return"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Row(accumulation_graph),
                ],
                align="top",
            ),
        ],
        fluid=True,
    )

    tab3_content = dbc.Container(
        [
            html.H1("Weights change"),
            html.Hr(),

            dbc.Row([dcc.Dropdown(
                final_portfolio.columns.tolist()[:-2],
                multi=True,
                value=top_assets,
                id="assets_dropdown",
                style={'color': 'black',
                       'width': '50%'}
                )]),


            dbc.Row(
                [
                    dbc.Row(cwd_graph),
                    dbc.Row(html.P(
                        """
                        Weights change graph is oriented to represent how the return is being distributed among the traded assets  as well
                        as providing the information how the capital would be split between the assets over the time compare to the initial
                        trade date. It allows visualization understanding which asset is generating positive return and which one is actually
                        generating the loss. An increase of asset area states the overall percentage of the capital is invested in this asset.
                        Primary the graph is focused on major sample group and the rest of assets are considered as minors in order to proved
                        understandable visualization, however if major sample is None then the graph will present all assets weights but
                        will also slow the backtest execution.
                        """
                    ))
                ],
                align="top",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Row(weights_graph),
                    dbc.Row(html.P(
                        """
                        Weights rebalancing graph serves only to visualize the percentage of the capital being invested in  the moment of
                        weights rebalancing. The total sum of the weights is always 100% since during rebalance the assets are getting the
                        weights according to the weights factor provided and total capital at that moment. Primary the graph is focused on
                        major sample group and the rest of assets are considered as minors in order to proved understandable visualization,
                        however if major sample is None then the graph will present all assets weights but will also slow the backtest execution.
                        """
                    ))
                ],
                align="top",
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(weights_changes_graph),
                    dbc.Col(weights_rebalance_graph)
                ],
                align="top",
            ),                 
        ],
        fluid=True,
    )

    tab4_content = dbc.Container(
        [
            html.H1("Monthly return"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Row(montly_graph),
                ],
                align="top",
            ),
        ],
        fluid=True,
    )

    tab5_content = dbc.Container(
        [
            html.H1("Drawdown"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Row(drawdown_graph),
                ],
                align="top",
            ),
        ],
        fluid=True,
    )

    tabs = dbc.Tabs(
        [
            dbc.Tab(tab1_content, label="Backtest results"),
            dbc.Tab(tab2_content, label="Accumulated return"),
            dbc.Tab(tab3_content, label="Weights change"),
            dbc.Tab(tab4_content, label="Monthly return"),
            dbc.Tab(tab5_content, label="Drawdown"),
        ]
    )

    app.layout = tabs

    app.title = "Plutus Backtest App!"

    @app.callback(
        Output("cwd_graph_tab", "figure"),
        Input("assets_dropdown", "value")
    )
    def assets_dropdown_cwd_tab(top_assets):
        cap_weights = _capitlised_weights_distribution(capitlised_weights_distribution=capitlised_weights_distribution,
                                                       major_assets=top_assets)
                                            
        return cap_weights

    @app.callback(
        Output("weights_graph", "figure"),
        Input("assets_dropdown", "value")
    )
    def assets_dropdown_weights_tab(top_assets):
        weights = _weights_distribution(portfolio_weights=portfolio_weights,
                                        major_assets=top_assets)
        
        return weights

    @app.callback(
        Output("cwd_graph_main", "figure"),
        Input("assets_dropdown", "value")
    )
    def assets_dropdown_cwd_main(top_assets):
        cap_weights = _capitlised_weights_distribution(capitlised_weights_distribution=capitlised_weights_distribution,
                                                       major_assets=top_assets)
        return cap_weights

    @app.callback(
        Output("download-portfolio-csv", "data"),
        Input("btn_portfolio_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def func(n_clicks):
        return dcc.send_data_frame(final_portfolio.to_csv, "final_portfolio_data.csv")

    @app.callback(
        Output("download-weights-csv", "data"),
        Input("btn_weights_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def func(n_clicks):
        return dcc.send_data_frame(portfolio_weights.to_csv, "portfolio_weights_data.csv")

    @app.callback(
        Output("download-sl-tp-csv", "data"),
        Input("btn_sl_tp_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def func(n_clicks):
        return dcc.send_data_frame(trade_breaker_frame.to_csv, "portfolio_sl_tp_data.csv")
    app.run_server(mode='external')