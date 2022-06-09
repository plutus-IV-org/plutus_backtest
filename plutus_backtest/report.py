import numpy as np
import pandas as pd
from tabulate import tabulate
from plutus_backtest.backtest import _security_list, _consolidated_table_detailed, _portfolio_construction, _stats
from plutus_backtest.plots import _accumulated_return, _weights_distribution, _capitlised_weights_distribution,\
    _monthly_return, _drawdown
from plutus_backtest.trade_breaker import _sl_tp
from plutus_backtest.benchmark import _benchmark_construction
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, dash_table

pd.options.mode.chained_assignment = None

def execution(asset, o_day, c_day, weights_factor=None,
                       take_profit=None,
                       stop_loss=None,
                       benchmark=None,
                       price_period_relation=None,
                       full_report = False):

    """ :Parameters:
               asset: str or list or series
                   Instruments taken into the consideration for the backtest.
               o_day: list of str or timestamps or series
                   Day/Days of the position opening.
               c_day: list of str or timestamps or series
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

    consolidated_table_detailed, auxiliar_df, security_list, weights_factor, price_close= _consolidated_table_detailed(security_list = security_list,
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
    final_portfolio, portfolio_weights, capitlised_weights_distribution, sl_dic, tp_dic = _portfolio_construction(detailed_return = consolidated_table_detailed,
                                                     security_list = security_list,
                                                     auxiliar_df = auxiliar_df,
                                                 weights_factor=weights_factor)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _sl_tp trade breaker
    if False in np.isinf(security_list[['take profit', 'stop loss']]).values:
        trade_breaker_frame = _sl_tp(sl_dic,tp_dic,price_close)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Calling _stats
    stats = _stats(final_portfolio)
    stats = stats.round(4)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Plotting

    if full_report == False:
        print(tabulate(stats.set_index('Indicators'), headers='keys', tablefmt='fancy_grid'))
        return _accumulated_return(final_portfolio = final_portfolio,
                                   benchmark_performance = benchmark_construction,
                                   benchmark_ticker = benchmark).show()

    else:
        accumulated = _accumulated_return(final_portfolio = final_portfolio,
                                          benchmark_performance = benchmark_construction,
                                          benchmark_ticker = benchmark)
        weights = _weights_distribution(portfolio_weights = portfolio_weights)
        cap_weights = _capitlised_weights_distribution(capitlised_weights_distribution = capitlised_weights_distribution)
        monthly = _monthly_return(final_portfolio = final_portfolio)
        drawdown = _drawdown(final_portfolio = final_portfolio)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Building app
    security_list.rename(columns={'company': 'Asset'}, inplace = True)
    security_list_short = security_list.head(10)

    app = Dash(external_stylesheets=[dbc.themes.QUARTZ])

    if False in np.isinf(security_list[['take profit', 'stop loss']]).values:

        table_1 = dbc.Table.from_dataframe(security_list_short)
        table_2 = dbc.Table.from_dataframe(stats)
        table_3 = dbc.Table.from_dataframe(trade_breaker_frame)


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
                    dcc.Graph(figure=cap_weights),
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
                    dcc.Graph(figure=weights)
                ]
            )
        ]
    )

    cwd_graph = dbc.Card(
        [
            html.Div(
                [
                    dcc.Graph(figure=cap_weights)
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



    tab1_content = dbc.Container(
        [
            html.H1("Backtest results"),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(sidebar, width=4),
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
            dbc.Row(
                [
                    dbc.Row(cwd_graph),
                    dbc.Row(html.P(
                        """
                        Weights change graph is oriented to represent how the return is being distributed among the traded assets  as well
                        as providing the information how the capital would be split between the assets over the time compare to the initial
                        trade date. It allows visualization understanding which asset is generating positive return and which one is actually
                        generating the loss. An increase of asset area states the overall percentage of the capital is invested in this asset.
                        """
                    ))
                ],
                align="top",
            ),
            dbc.Row(),
            dbc.Row(
                [
                    dbc.Row(weights_graph),
                    dbc.Row(html.P(
                        """
                        Weights rebalancing graph serves only to visualize the percentage of the capital being invested in  the moment of
                        weights rebalancing. The total sum of the weights is always 100% since during rebalance the assets are getting the
                        weights according to the weights factor provided and total capital at that moment.
                        """
                    ))
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

    app.run_server(debug=True, port=8888)
