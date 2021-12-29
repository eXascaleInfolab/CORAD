import plotly.express as px

import pandas as pd

import numpy as np

import plotly.graph_objects as go

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

# fig = px.line(df, x='Date', y='AAPL.High')
# fig.show()

# Create traces
N = 100
x = df['Date'].to_numpy()
arr = [ 'AAPL.High', 'AAPL.Low','AAPL.Close','AAPL.Adjusted']
# arr = [ 'dn','mavg','up']

# Ys = []

fig = go.Figure()
i = 0

fig.update_xaxes(title_font=dict(size=26, family='Courier', color='crimson'))
fig.update_layout(

    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text="Time",
            font=dict(
                family="Courier New, monospace, bold",
                size=24,
                color="black"
            )
        )
    ),
    yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text="Apple Stock Price ($)",
            font=dict(
                family="Courier New, monospace, bold",
                size=24,
                color="black",
            )
        )
    ),
    legend=go.layout.Legend(
        x=0,
        y=1,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=18,
            color="black"
        ),
        bgcolor="LightSteelBlue",
        bordercolor="Black",
        borderwidth=2
    )
)


for y in arr:
    # Ys.append(df[y].to_numpy())
    fig.add_trace(go.Scatter(x=x, y=df[y].to_numpy()+ i,
                             mode='lines+markers',
                             name=y))
    i += 20




# fig.add_trace(px.line(df, x='Date', y='AAPL.High'))

# fig.add_trace(go.Scatter(x=random_x, y=random_y2,
#                     mode='markers', name='markers'))

fig.show()