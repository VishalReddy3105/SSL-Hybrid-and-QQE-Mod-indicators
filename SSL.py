import pandas as pd
import numpy as np
import plotly.offline as pyo
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import talib
import ta
import plotly.graph_objs as go
import plotly.subplots as sp

# Load data from CSV file
df = pd.read_csv('./datafinal.csv')

df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

# Compute SSL Hybrid indicator
period = 10
p2=5
dev=2
ssl_u = (df['High'] + df['Low']) / 2 + dev * np.sqrt((df['High'] - df['Low']) ** 2 / period)
ssl_d = (df['High'] + df['Low']) / 2 - dev * np.sqrt((df['High'] - df['Low']) ** 2 / period)

ssl_up = talib.HT_TRENDLINE(ssl_u)
ssl_down = talib.HT_TRENDLINE(ssl_d)      
ema = talib.EMA(df['Close'], timeperiod=period)
oscillator = ssl_up - ssl_down
ssl_fast = talib.EMA(oscillator, timeperiod=period)
ssl_slow = talib.EMA(ssl_fast, timeperiod=period)
ssl_hybrid = np.where(ssl_fast > ssl_slow, 1, 0)

bollinger_period = 20
bollinger_deviation = 2
bb = BollingerBands(df['Close'], window=bollinger_period, window_dev=bollinger_deviation)
df['bb_hband']= bb.bollinger_hband()
df['bb_lband']= bb.bollinger_lband()


# Calculate the MACD and signal line
df['26 EMA'] = df['Close'].ewm(span=26).mean()
df['12 EMA'] = df['Close'].ewm(span=12).mean()
df['MACD'] = df['12 EMA'] - df['26 EMA']
df['Signal Line'] = df['MACD'].ewm(span=9).mean()

# Calculate the MACD histogram
df['MACD Histogram'] = df['MACD'] - df['Signal Line']

rsi_period = 14
rsi= RSIIndicator(df['Close'], rsi_period)
df['rsi']=rsi.rsi()

# Compute buy and sell signals
df['Signal'] = None
df['sign']=0
df['Sign']=0

df.loc[(df['rsi'] < 30) & (df['Close'] < df['bb_lband']) & (df['MACD'] > df['Signal Line'])  ,'sign']= 1
df.loc[(df['rsi'] < 30) & (df['Close'] < df['bb_lband']) & (df['MACD'] < df['Signal Line']) ,'sign']= -1


buy_signals = df[df['sign'] == 1]
sell_signals = df[df['sign'] == -1]

# Create candlestick chart with SSL up and down traces, and buy and sell arrow signals
candle = go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Candlestick')
ssl_up_trace = go.Scatter(x=df.index, y=ssl_up, mode='lines', line=dict(color='blue'), name='SSL Up')
ssl_down_trace = go.Scatter(x=df.index, y=ssl_down, mode='lines', line=dict(color='red'), name='SSL Down')
bb_upper = go.Scatter(x=df.index, y=df['bb_hband'], name='BB Upper', line=dict(color='#ccc', width=1, dash='dot'))
bb_lower = go.Scatter(x=df.index, y=df['bb_lband'], name='BB Lower', line=dict(color='#ccc', width=1, dash='dot'))

data = [candle, ssl_up_trace, ssl_down_trace]

data.append(bb_lower)
data.append(bb_upper)

# Create volume bars
volume = go.Bar(x=df['datetime'], y=df['Volume'], name='Volume')

# Create subplots for candlestick chart and volume bars
fig = sp.make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05)
fig.add_traces(data, rows=1, cols=1)
fig.add_trace(volume, row=3, col=1)

fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['Close'],
                    mode='markers',
                    marker=dict(symbol='triangle-up', size=10, color='yellow'),
                    name='Buy'))

fig.add_trace(go.Scatter(x=sell_signals.index, y=sell_signals['Close'],
                    mode='markers',
                    marker=dict(symbol='triangle-down', size=10, color='black'),
                    name='Sell'))

fig.add_trace(go.Scatter(x=df['datetime'], y=df['MACD'], mode='lines', name='MACD'), row=2, col=1)
fig.add_trace(go.Scatter(x=df['datetime'], y=df['Signal Line'], mode='lines', name='Signal Line'), row=2, col=1)
fig.add_trace(go.Bar(x=df['datetime'], y=df['MACD Histogram'], name='MACD Histogram'), row=2, col=1)

# Update layout
# fig.update_layout(xaxis_rangeslider_visible=False, height=600)
fig.update_layout(width=1750, height=980,xaxis_rangeslider_visible=False)
fig.write_html("./SSL-Hybrid.html")
# Show plot
fig.show()
