import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import re

# Step 1. Launch the application
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

# Step 2. Import the dataset
df = pd.read_csv("../../data/dataset.csv")

#Reduz o dataset a partir dos primeiros caso
dfc = df[df['China_confirmed']>0]
recent_date =  dfc['True'].max()
old_date = df['True'].min()

recent_year = int(re.split('-',recent_date)[0])
old_year = int(re.split('-',old_date)[0])
years = [i for i in range(old_year, recent_year+1)]

month = ['Jan.','Feb.','Mar.','Apr.','May','June','July','Aug.','Sept.','Oct.','Nov.','Dec.']
month_mark = {i+1 : month[i] for i in range(0, 12)}

country = ['China','Italy', 'Iran','Spain','Germany','USA','France','S. Korea','Switzerland','UK','Portugal']

# Step 4. Create a Dash layout
app.layout = html.Div(
        html.Div([
            dbc.Row(
                [
                    dbc.Col( 
                        dcc.Markdown(
                            '''**País**'''
                        ),
                        width=1
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id='yaxis-column',
                            options=[{'label': i, 'value': i} for i in country],
                            value='Portugal'
                        ),
                        width=3
                    )
                ],
                no_gutters=True,
                justify="start"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Markdown(
                            '''**Analisar**'''
                        ),
                        width=1
                    ),
                    dbc.Col(
                        dcc.Checklist(
                            id = "yaxis-type",
                            options=[
                                {'label': 'Confirmed', 'value': 'confirmed'},
                                {'label': 'Deaths', 'value': 'deaths'},
                            ],
                            value=['confirmed', 'deaths'],
                        )
                    )
                ],
                no_gutters=True
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Tabs(
                            [
                                dcc.Tab(label='Número de caso acumulados', children=[
                                    html.Div(id='acumulados-graph')
                                ]),
                                dcc.Tab(label='Taxa de crescimento diária', children=[
                                    html.Div(id='percentagem-graph')
                                ])
                            ],
                            colors={
                                "border": "white",
                                "primary": "gold",
                                "background": "cornsilk"
                            }
                        )
                    )
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Markdown(
                            '''**Dia**'''
                        ),
                        width=1
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id='time-down',
                            options=[{'label': i, 'value': i} for i in dfc['True']],
                            value=recent_date
                        ),
                        width=3
                    )
                ],
                no_gutters=True,
                justify="start"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(
                            id='compare-countries',
                        )
                    )
                ],
                justify="start"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Markdown(
                            '''**Ano**'''
                        ),
                        width=1
                    ),
                    dbc.Col(
                        dcc.Dropdown(
                            id='year-cripto',
                            options=[{'label': i, 'value': i} for i in years],
                            value='2020'
                        ),
                        width=3       
                    ),
                ],
                no_gutters=True
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Markdown(
                            '''**Criptomoedas**'''
                        ),
                        width=1
                    ),
                    dbc.Col(
                        dcc.Checklist(
                            id = "cripto-type",
                            options=[
                                {'label': 'Bitcoin', 'value': 'bitcoin_usd'},
                                {'label': 'Ethereum', 'value': 'ethereum_usd'},
                                {'label': 'Ripple', 'value': 'ripple_usd'},
                                {'label': 'Litecoin', 'value': 'litecoin_usd'}
                            ],
                            value=['bitcoin_usd', 'ethereum_usd', 'ripple_usd', 'litecoin_usd'],
                        )
                    )
                ],
                no_gutters=True,
                justify="start"
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(id='compare-cripto')
                    )
                ],
                justify="start"
            ),
            dbc.Row(
                [
                    dbc.Col(
                       dcc.Markdown(
                            '''**Meses**'''
                        ),
                       width="auto" 
                    ),
                    dbc.Col(
                        dcc.RangeSlider(
                            id = 'slider',
                            marks = month_mark,
                            min = 1,
                            max = 12,
                            value = [1, 3]
                        ) 
                    )
                ]
            )
        ]
    )
    
)





@app.callback(
    Output('acumulados-graph', 'children'),
    [Input('yaxis-column', 'value'),
     Input('yaxis-type', 'value')])
def update_graph_acumulados(yaxis_column_name,yaxis_type):
    dff = df[df[yaxis_column_name + "_confirmed"] > 0]

    return [
        dcc.Graph(
            figure={
                "data": [
                            go.Scatter(x = dff['True'],y = dff[yaxis_column_name + "_" + t],mode = "lines",name=t)for t in yaxis_type
                        ],
                'layout': {
                    'title': yaxis_column_name,
                    'height': 450,
                    'margin': {'l': 38, 'r': 10, 't': 40},
                    'yaxis': {'type': 'linear', 'title': 'Valores em unidades'},
                    'xaxis': {'showgrid': False}
                }
            },
        )
    ]

@app.callback(
    Output('percentagem-graph', 'children'),
    [Input('yaxis-column', 'value'),
     Input('yaxis-type', 'value')])
def update_graph_percentagem(yaxis_column_name, yaxis_type):
    y_colum1 = yaxis_column_name + "_confirmed"
    y_colum2 = yaxis_column_name + "_deaths"   
    dfp = df[df[y_colum1]>0]

    val = {}
    val['confirmed'] = obtemP(dfp,y_colum1)
    val['deaths'] = obtemP(dfp,y_colum2)
    min = dfp['True'].min()
    dfp = dfp[dfp['True']>min]
    return [
        dcc.Graph(
            figure={
                "data": [
                     go.Scatter(x = dfp['True'],y = val[t],mode = "lines",name=t)for t in yaxis_type
                ],
                'layout': {
                    'title': yaxis_column_name + " ",
                    'height': 450,
                    'margin': {'l': 30, 'r': 10, 't': 40},
                    'yaxis': {'type': 'linear', 'title': 'Valores em %'},
                    'xaxis': {'showgrid': False}
                }
            
            }
        )
    ]

def getValues(col, dfa):
    l = []
    for a in col:
        if len(l) == 0: 
            l = dfa[a]
        else:
            l = np.concatenate((l,dfa[a]),axis=0)
    return l

@app.callback(
    Output('compare-countries', 'figure'),
    [Input('time-down', 'value')])
def update_graph_countries(day):
    dfa = df[df['True'] == day]
    colC = ['China_confirmed', 'Italy_confirmed','Iran_confirmed', 'Spain_confirmed','Germany_confirmed', 'USA_confirmed','France_confirmed','S. Korea_confirmed','Switzerland_confirmed','UK_confirmed','Portugal_confirmed']
    colD = ['China_deaths', 'Italy_deaths','Iran_deaths', 'Spain_deaths','Germany_deaths', 'USA_deaths','France_deaths','S. Korea_deaths','Switzerland_deaths','UK_deaths','Portugal_deaths']
    lc = getValues(colC,dfa)
    ld = getValues(colD,dfa)
    return {
        'data': [
                {'x': country, 'y': lc, 'type': 'bar', 'name': 'Confirmed'},
                {'x': country, 'y': ld, 'type': 'bar', 'name': 'Daths'},
            ],
        'layout': {
            'title': 'Aumento diário',
            'height': 325,
            'margin': {'l': 30, 'r': 10, 't': 40},
        }
    }

def percentagem(present, past):
    if(past==0):
        return 0
    p = (present-past)/past
    return p*100

def obtemP(dfp,col):
    flag = True
    past = 0
    l = []
    for row in dfp[col]:
        if flag:
            flag = False
            past = row
        else:
            present = int(row)
            p = percentagem(present,past)
            l.append(p)
            past = present
    return l


@app.callback(
    Output('compare-cripto', "children"),
    [Input('cripto-type', 'value'),
    Input('year-cripto', 'value'),
    Input('slider','value')] 
)
def update_graph_cripto(cripto,year,month):
    ml = str(month[0]).zfill(2)
    mu = str(month[1] + 1).zfill(2)
    date_min = str(year) + "-" + ml + "-" + "01"
    date_max = str(year) + "-" + mu + "-" + "01"

    dfcr1 = df[df['True'] >= date_min]
    dfcr = dfcr1[dfcr1['True'] < date_max]
    return [
        dcc.Graph(
            figure={
                "data": [
                     go.Scatter(x = dfcr['True'],y = dfcr[cri],mode = "lines",name=cri)for cri in cripto
                ],
                "layout": {
                        "title": "Preço das criptomoedas",
                        "xaxis": {"automargin": True},
                        "yaxis": {"automargin": True,"type":"log"},
                        "height": 450,
                        "margin": {"t": 40,"l": 10, "r": 10},
                },
            },
        )
    ]


# Step 6. Add the server clause
if __name__ == '__main__':
    app.run_server(debug = True)
