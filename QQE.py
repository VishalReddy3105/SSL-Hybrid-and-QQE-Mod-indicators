import pandas as pd
import plotly.graph_objects as go


df = pd.read_csv('./datafinal.csv')


period = 14
df['EMA'] = df['Close'].ewm(span=period).mean()


delta = df['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(period).mean()
avg_loss = loss.rolling(period).mean()
rs = avg_gain / avg_loss
df['RSI'] = 100 - (100 / (1 + rs))

exp1 = df['Close'].ewm(span=12, adjust=False).mean()
exp2 = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = exp1 - exp2
df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

df['sRSI'] = df['RSI'].ewm(span=period).mean()

df['MACD_diff'] = df['MACD'] - df['Signal']
df['QQE'] = df['sRSI'] * df['MACD_diff'].ewm(span=period).mean()

df['QQE_Mod'] = df['QQE'].ewm(span=period).mean()

trend = []
for i in range(1, len(df)):
    if df['QQE_Mod'][i] > df['QQE_Mod'][i-1] and df['QQE_Mod'][i] > 0:
        trend.append('Bullish')
    elif df['QQE_Mod'][i] < df['QQE_Mod'][i-1] and df['QQE_Mod'][i] < 0:
        trend.append('Bearish')
    else:
        trend.append('Consolidating')
trend.insert(0, 'Consolidating')
df['Trend'] = trend

df = df[df['QQE_Mod'] != 0]

colors = ['red' if trend == 'Bearish' and QQE_Mod < 0 else 'gray' if trend == 'Consolidating' else 'green' for trend, QQE_Mod in zip(df['Trend'], df['QQE_Mod'])]
fig = go.Figure(data=[go.Bar(x=df.index, y=df['QQE_Mod'], marker={'color': colors}, hovertemplate='<b>QQE Mod:</b> %{y:.2f}<extra></extra>')])
fig.update_traces(selector=dict(type='bar'), marker_line_width=0)
fig.update_layout(title='QQE Mod Indicator for Bitcoin Price', xaxis_title='Date', yaxis_title='QQE Mod', yaxis_tickformat='.2f')
fig.write_html("./QQE-Mod.html")
fig.show()
