import pandas as pd
import plotly.subplots as sp
import plotly.express as px

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Accumulated return
def _accumulated_return(final_portfolio):
    df_accum = final_portfolio
    return df_accum

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Drawdown
def _drawdown(final_portfolio):
    port_performance_drawdown = final_portfolio
    port_performance_drawdown = port_performance_drawdown.clip(upper=0)
    port_performance_drawdown = port_performance_drawdown.drop(columns=['Sum', 'Accumulation'])
    # port_performance_drawdown = abs(port_performance_drawdown)
    port_performance_drawdown['Sum'] = port_performance_drawdown.sum(axis=1)
    port_performance_drawdown['Accumulation'] = (port_performance_drawdown['Sum'].cumsum()) * 100
    df_drawdown = port_performance_drawdown
    df_drawdown = df_drawdown.round(decimals=3)
    return df_drawdown

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Monthly return
def _monthly_return(final_portfolio):
    mon = []
    df_monthly = final_portfolio
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
    df_montly.columns = ["Result"]
    return df_montly

# ----------------------------------------------------------------------- #
# Create figures in Express


# ----------------------------------------------------------------------- #
# Add benchmark if triggered

def _plotting(accumulated_return, drawdown, monthly_return, portfolio_weights, benchmark_performance, benchmark_ticker = None):

    df_accum = accumulated_return
    df_drawdown = drawdown
    df_montly = monthly_return


    if benchmark_ticker is not None:
        df_bench = benchmark_performance
        df_accum = pd.merge(df_accum.copy(), df_bench["Bench_Accumulation"], how='right', left_index=True,
                            right_index=True)
        # df_accum = df_accum.fillna(0)
        df_accum["Bench_Accumulation"] = df_accum["Bench_Accumulation"].fillna(method='ffill')
        df_accum['Accumulation'] = df_accum['Accumulation'].ffill()
        df_accum.fillna(value=0, inplace=True)
        # Execution plot - Accumulation with benchmark
        df_accum_fig1 = df_accum.astype(float)
        df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
        df_accum_fig1 = df_accum_fig1.round(2)
        df_accum_fig1 = df_accum_fig1.fillna(0)
    
        fig1 = px.line(df_accum_fig1,
                       x=df_accum_fig1.index,
                       y=df_accum_fig1["Accumulation"],
                       title="Accumulated return",
                       hover_data=df_accum_fig1.columns[:-3])  # show all columns values excluding last 3
    
        fig1.update_layout(xaxis_title="Date")
        fig1.update_traces(name='Portfolio',
                           showlegend=True)
    
        fig1.add_scatter(x=df_accum_fig1.index,
                         y=df_accum_fig1["Bench_Accumulation"],
                         mode='lines',
                         name="Benchmark")
    else:
    
        df_accum_fig1 = df_accum.astype(float)
        df_accum_fig1.iloc[:, :-2] = (df_accum_fig1.iloc[:, :-2] * 100)
        df_accum_fig1 = df_accum_fig1.round(2)
        fig1 = px.line(df_accum_fig1,
                       x=df_accum_fig1.index,
                       y=df_accum_fig1["Accumulation"],
                       hover_data=df_accum_fig1.columns[:-2])  # show all columns values excluding last 2
    
    weights_df = portfolio_weights
    weights_df["Total Weights"] = weights_df.sum(axis=1)
    weights_df = weights_df[weights_df["Total Weights"] != 0]
    weights_df = weights_df.drop("Total Weights", axis=1)
    weights_df = abs(weights_df)
    fig2 = px.area(weights_df * 100,
                   x=weights_df.index,
                   y=weights_df.columns)
    
    df_montly_fig3 = df_montly.astype(float)
    color = []
    for i in df_montly_fig3["Result"]:
        if i < 0:
            color.append('red')
        else:
            color.append('green')
    df_montly_fig3["color"] = color
    df_montly_fig3 = df_montly_fig3.round(2)
    fig3 = px.bar(df_montly_fig3,
                  x=df_montly_fig3.index,
                  y=df_montly_fig3["Result"],
                  color=df_montly_fig3["color"],
                  color_discrete_sequence=df_montly_fig3["color"].unique())
    
    df_drawdown_fig2 = df_drawdown.astype(float)
    df_drawdown_fig2.iloc[:, :-2] = (df_drawdown_fig2.iloc[:, :-2] * 100)
    df_drawdown_fig2 = df_drawdown_fig2.round(2)
    fig4 = px.line(df_drawdown_fig2,
                   x=df_drawdown_fig2.index,
                   y=df_drawdown_fig2["Sum"] * 100,
                   hover_data=df_drawdown_fig2.columns[:-2])  # show all columns values excluding last 2
    
    # For as many traces that exist per Express figure, get the traces from each plot and store them in an array.
    # This is essentially breaking down the Express fig1, 2, 3 into it's traces
    figure1_traces = []
    figure2_traces = []
    figure3_traces = []
    figure4_traces = []
    
    for trace in range(len(fig1["data"])):
        figure1_traces.append(fig1["data"][trace])
    
    for trace in range(len(fig2["data"])):
        figure2_traces.append(fig2["data"][trace])
    
    for trace in range(len(fig3["data"])):
        figure3_traces.append(fig3["data"][trace])
    
    for trace in range(len(fig4["data"])):
        figure4_traces.append(fig4["data"][trace])
    
    # Create a 1x4 subplot
    this_figure = sp.make_subplots(rows=4, cols=1,
                                   vertical_spacing=0.1,
                                   shared_xaxes=False,
                                   shared_yaxes=False,
                                   subplot_titles=("Accumulative return",
                                                   "Weights distribution",
                                                   "Monthly return",
                                                   "Drawdown"
                                                   ))
    
    for traces in figure1_traces:
        this_figure.append_trace(traces, row=1, col=1)
    
    for traces in figure2_traces:
        this_figure.append_trace(traces, row=2, col=1)
    
    for traces in figure3_traces:
        this_figure.append_trace(traces, row=3, col=1)
    
    for traces in figure4_traces:
        this_figure.append_trace(traces, row=4, col=1)
    
    this_figure.update_layout(hovermode='x', showlegend=False)
    # Prefix y-axis tick labels with % sign
    this_figure.update_yaxes(tickprefix="%")
    this_figure['layout'].update(height=800, title='Plotting results')
    #this_figure['layout'].update(title='Plotting results')
    return this_figure









