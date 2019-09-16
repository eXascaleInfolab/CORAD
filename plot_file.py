import plotly.express as px

import pandas as pd

import numpy as np

import plotly.graph_objects as go

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df = pd.read_csv('paper-example/daily.csv')

# fig = px.line(df, x='Date', y='AAPL.High')
# fig.show()

# Create traces
N = 100
# x = df['Date'].to_numpy()
# arr = [ 'AAPL.High', 'AAPL.Low','AAPL.Close','AAPL.Adjusted']
# arr = [ 'dn','mavg','up']

# Ys = []

fig = go.Figure()
for i in range(4):
    # Ys.append(df[y].to_numpy())
    fig.add_trace(go.Scatter( y=df.iloc[:,i].to_numpy(),
                             ))



# fig.add_trace(px.line(df, x='Date', y='AAPL.High'))

# fig.add_trace(go.Scatter(x=random_x, y=random_y2,
#                     mode='markers', name='markers'))

fig.show()