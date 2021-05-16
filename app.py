# -*- coding: utf-8 -*-

# TICKER별 Volume, Return 그래프 산출함수
# 기간 정보를 입력합니다 (1차)
# TICKER 정보를 입력합니다. (2차)
# 데이터를 호출하여 linegraph를 산출합니다.  (3차)
# linegraph의 hoverdata에 해당하는 데이터 값을 piechart로 산출합니다.  (3차)

import dash  # Dash 1.16 or higher
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from datetime import date
import datetime
import pandas_datareader.data as web
import dash_bootstrap_components as dbc
import dash_table

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# TICKER별 데이터 호출
def get_data(TICKER,start,end):
    dfs = web.DataReader(TICKER, 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:, 'TICKER'] = TICKER
    df = dfs
    # 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
    df = df.reset_index().rename(columns={"index": "id"})
    df.to_csv('pricevolume.csv', index=False, encoding='cp949')
    df = pd.read_csv('....../pricevolume.csv')
    return df

# 정해진 그룹 데이터 호출
def get_data_group(start,end):
    TICKER = ['AAPL', 'TSLA', 'MSFT', 'AMZN', 'GOOGL', 'FB', 'NVDA', 'BABA', 'NFLX', 'XOM']
    dfs = web.DataReader(TICKER[0], 'yahoo', start, end)
    dfs.reset_index(inplace=True)
    dfs.set_index("Date", inplace=True)
    dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
    dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
    dfs = dfs.dropna()
    dfs.loc[:, 'TICKER'] = TICKER[0]
    df = dfs
    for i in range(1, len(TICKER)):
        dfs = web.DataReader(TICKER[i], 'yahoo', start, end)
        dfs.reset_index(inplace=True)
        dfs.set_index("Date", inplace=True)
        dfs['Return'] = (dfs['Close'] / dfs['Close'].shift(1)) - 1
        dfs['Return(cum)'] = (1 + dfs['Return']).cumprod()
        dfs = dfs.dropna()
        dfs.loc[:, 'TICKER'] = TICKER[i]
        df = df.append(dfs)
    # 데이터타입(Date)변환 문제로 csv 저장 후, 다시 불러옵니다. (파일 경로 설정 필요!!)
    df = df.reset_index().rename(columns={"index": "id"})
    df.to_csv('pricevolume.csv', index=False, encoding='cp949')
    df = pd.read_csv('..../pricevolume.csv')
    return df

# Default
start =  date(2020, 12, 1)
end = datetime.datetime.now()
df = get_data_group(start,end)

app.layout = html.Div([
    html.H3("Ticker별 Volume, Return"),
    html.Br(),
    # dcc.DatePickerRange(
    #     id="my-date-picker-range",
    #     min_date_allowed=date(2021, 1, 1),
    #     start_date_placeholder_text='2021-01-01',
    #     end_date_placeholder_text='2021-05-11',
    #     display_format='YYYY-MM-DD'
    # ),
    html.Br(),
    html.H4(" * Sector, TICKER 입력"),
    dcc.Dropdown(
        id='dropdown-TICKER',
        options=[{'label': s, 'value': s} for s in df.TICKER.unique()],
        multi=True,
        value= df.TICKER.unique()[0:2],
        clearable=False),
    html.Div([
        dcc.Graph(id='pie-graph', figure={}, className='five columns'),
        dcc.Graph(id='my-graph', figure={}, clickData=None, hoverData=None,
                  config={
                      'staticPlot': False,
                      'scrollZoom': True,
                      'doubleClick': 'autosize',
                      'showTips': False,
                      'displayModeBar': True,
                      'watermark': True,
                  },
                  className='five columns'
                  )
    ])
])

@app.callback(
    Output('my-graph','figure'),
    [Input('dropdown-TICKER','value')]
)
def update_graph(TICKER_chosen):
    # df = get_data_group(start_date,end_date)
    dff = df[df.TICKER.isin(TICKER_chosen)]
    fig = px.line(data_frame=dff, x='Date', y='Return(cum)', color='TICKER',
                  custom_data=['TICKER', 'Return', 'Volume', 'Close'],  title= 'Return for TICKER')
    fig.update_traces(mode='lines+markers')
    return fig

@app.callback(
    Output('pie-graph','figure'),
    [Input('my-graph','hoverData'),
    Input('dropdown-TICKER', 'value')]
)
def update_side_graph(hov_data, TICKER_chosen):
    # df = get_data_group(start_date, end_date)
    if hov_data is None:
        dff2 = df[df.TICKER.isin(TICKER_chosen)]
        dff2 = dff2[dff2.Date == '20210101']
        fig2 = px.pie(data_frame=dff2, values='Volume', names='TICKER',
                      title='Volume for 20210101')
        return fig2
    else:
        dff2 = df[df.TICKER.isin(TICKER_chosen)]
        hov_year = hov_data['points'][0]['x']
        dff2 = dff2[dff2.Date == hov_year]
        fig2 = px.pie(data_frame=dff2, values='Volume', names='TICKER', title=f'Volume for: {hov_year}')
        return fig2

if __name__ == "__main__":
    app.run_server(debug=True, port = '7060')