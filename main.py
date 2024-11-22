from queue import Queue
from threading import Thread, Lock
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input, State, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
from grafico_produto import GraficoProduto
import dash
from database import select, obterProdutos, obterVendas, saveDB, get_options_from_db, historico, obter_config, saveConfig
from datetime import timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from pmdarima.arima import auto_arima

lock = Lock()

df = pd.DataFrame(columns=['quant', 'data', 'id_produto'])
df = select()

produtos = pd.DataFrame(columns=['id_produto', 'nome_produto', 'quant_max_prateleira'])
produtos = obterProdutos()

df_bar = pd.DataFrame(columns=['id_produto', 'quant_total'])
df_bar = obterVendas()

selected_itemsGeral = []

store = {"result": ""}

def comprarProduto(queue, id, data_atual):
    while True:
        tempo = geracaoTempo(id)
        quant = geracaoQuant(id)
        time.sleep(0.5)
        data_atual, date = gerarData(data_atual, tempo)
        data = {"quant": quant, "data": date}
        queue.put(data)

def obterEstoqueAtual():
    try:
        ultimo_registro = df.groupby('id_produto')['quant'].last().reset_index()
        quant_estoque_dict = ultimo_registro.set_index('id_produto')['quant'].to_dict()
        quant_estoque = [quant_estoque_dict.get(produto['id_produto'], produto['quant_max_prateleira']) for _, produto in produtos.iterrows()]
    except:
        quant_estoque = [produto['quant_max_prateleira'] for produto in produtos]
    return quant_estoque

def obterData():
    try:
        ultimo_registro = df.groupby('id_produto')['data'].last().reset_index()
        data_dict = ultimo_registro.set_index('id_produto')['data'].to_dict()
        data = [data_dict.get(produto_id, datetime.now()) for produto_id in produtos['id_produto']]
    except:
        data = [datetime.now() for i in range(len(produtos))]
    return data

def gerarData(data_atual, tempo):
    tempo = converteFloatMinuto(tempo)
    data_atual = data_atual + tempo
    dt_string = data_atual.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return data_atual, dt_string

def converteFloatMinuto(tempo):
    minutos = int(tempo)
    segundos = int((tempo - minutos) * 60)

    return timedelta(minutes=minutos, seconds=segundos)

def geracaoTempo(id):
    return 5*random.expovariate(1)
    
def geracaoQuant(id):
    if id%2 == 0:
        quant = int(1.5*np.random.poisson(6))
    else:
        quant = 2*np.random.poisson(6)
    return quant

def generate_random_numbers(queue, quant_estoque, id_produto):
    global df
    quant_total = df_bar.loc[df_bar['id_produto'] == id_produto, 'quant_total']
    while quant_estoque > 0:
        data = queue.get()
        quant = data['quant']
        date = data['data']
        quant_estoque = quant_estoque - quant
        quant_total = quant_total + quant
        if quant_estoque < 0:
            quant = quant + quant_estoque
            quant_estoque = 0
        new_row = {'quant': quant_estoque, 'data': date, 'id_produto': id_produto}
        with lock:
            df.loc[len(df)] = new_row
        df_bar.loc[df_bar['id_produto'] == id_produto, 'quant_total'] = quant_total
        saveDB(quant, date, quant_estoque, id_produto)
        if quant_estoque == 0:
            quant_estoque = produtos.loc[produtos['id_produto'] == id_produto]['quant_max_prateleira'].values[0]

app = Dash(suppress_callback_exceptions=True, external_stylesheets=["https://fonts.googleapis.com/icon?family=Material+Icons", 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css', dbc.themes.BOOTSTRAP])

default_layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='url2', refresh=False),
        dcc.Store(id='dropdown-values'),
        html.Div([
                html.Button(html.Span("home", className="material-icons"), id='botao-home',),
                html.Button(html.Span("add", className="material-icons"), id='botao-add-produtos'),
                html.Button(html.Span("query_stats", className="material-icons"), id='botao-previsao'),
                html.Button(html.Span("settings", className="material-icons"), id='botao-config'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
        html.Div(id='page-content')
    ])

def main(): 
    quant_estoque = obterEstoqueAtual()
    data_atual = obterData()
    
    queue = [Queue() for i in range(len(produtos))]
    produto = ["" for i in range(len(produtos))]
    thread = ["" for i in range(len(produtos))]
    
    for i in range(len(produtos)):
        produto[i] = Thread(target=comprarProduto, args=(queue[i], produtos["id_produto"].loc[i], data_atual[i] ))
        produto[i].start()
        
        thread[i] = Thread(target=generate_random_numbers, args=(queue[i], quant_estoque[i], produtos["id_produto"].loc[i] ))
        thread[i].start()

    app.layout = default_layout
        
    app.run(debug=False, use_reloader=False)
    
@callback(
    Output('url', 'pathname'),
    [Input('botao-home', 'n_clicks'),
     Input('botao-previsao', 'n_clicks'),
     Input('botao-config', 'n_clicks'),
     ],
    Input('url', 'pathname'),
)
def redirecionar_page(n1, n3, n4, pathname):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'botao-home' and n1:
        return '/home'
    elif button_id == 'botao-previsao' and n3:
        return '/previsao'
    elif button_id == 'botao-config' and n4:
        return '/config'

    return pathname

#------------------------------------------------------ Páginas ----------------------------------------------------------------#

@callback(Output('page-content', 'children'),
            Input('url', 'pathname'))
def display_page(pathname):
    configs = obter_config()
    if pathname == '/home' or pathname == '/':
        global selected_itemsGeral
        dropdown_options = get_options_from_db()
        dropdown_options.insert(0, {'label': 'Selecionar Todos', 'value': 'ALL'})
        layout = html.Div([html.H1(children='Monitoramento de Consumo', style={'textAlign':'center'}),
                            dcc.Interval(id='interval-start', interval=1, n_intervals=0, max_intervals=1),
                            dbc.Modal(
                                [
                                    dcc.Interval(id='interval-dropdown', interval=1, n_intervals=0, max_intervals=1),
                                    dbc.ModalHeader(dbc.ModalTitle("Adicionar produtos")),
                                    dbc.ModalBody(dcc.Dropdown(
                                                id='dropdown-produto',
                                                options=dropdown_options,
                                                placeholder="Selecione uma opção",
                                                value=selected_itemsGeral,
                                                multi=True,
                                                style={'width': '100%'}
                                            ),),
                                    dbc.ModalFooter(
                                            html.Div([
                                            html.Button('Adicionar', id='botao-criar', style={'width': '150px', 'height': '50px', 'font-size': '25px'}),
                                        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
                                    ),
                                ],
                                id="modal",
                                is_open=False,
                                size="lg",
                                backdrop=True,
                                keyboard=True,
                                centered=True,
                            ),
                            html.Div(id='graphs-container', style={'display': 'flex', 'flex-wrap': 'wrap'}, className="row"),
                            dcc.Interval(
                                id='interval-component',
                                interval=500,
                                n_intervals=0,
                            ),
                            html.Div([dcc.Graph(
                                id='bar-graph',
                            )],id='bar_graph_div', style={'display': 'block' if configs['grafico_barras'][0] else 'none'}),
                            html.Div(id='dynamic-content', style={'textAlign':'center', 'display': 'block' if configs['previsao_home'][0] else 'none'}),
                            dcc.Interval(
                                id='interval-previsao',
                                interval=3500,
                                n_intervals=0,
                            ),
                            dcc.Interval(
                                id='interval-check',
                                interval=500,
                                n_intervals=0,
                            ),
                            dcc.Store(id='ranking-values'),
                            ]),
        return layout
    elif pathname == '/previsao':
        dropdown_options = get_options_from_db()
        layout2 = html.Div([html.H1(children='Previsão', style={'textAlign':'center'}),
                            html.Div([
                            html.Div([html.P(children='Produto', style={'textAlign':'center'}),
                            dcc.Dropdown(
                                id='dropdown-produto-prever',
                                options=dropdown_options,
                                placeholder="Selecione um produto",
                                value=selected_itemsGeral,
                                multi=False,
                                style={'width': '200px'}
                            )],style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px'}),
                            html.Div([html.P(children='Intervalo de previsão (min)'),
                            dcc.Input(id='input-intervalo',type='text', value=configs['intervalo_padrao'][0], placeholder="Insira o intervalo"),
                                ],style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px', 'text-align': 'center'}),
                            html.Button('Prever', id='botao-prever', style={'width': '150px', 'height': '50px', 'font-size': '25px', 'alignSelf': 'center'}),
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'margin-bottom': "25px"}),
                            html.Div(id='graphs-container-previsao', style={'display': 'flex', 'flex-wrap': 'wrap'}, className="row"),
                            ])
        return layout2
    elif pathname == '/config':
        layout2 = html.Div([html.H1(children='Configurações', style={'textAlign':'center'}),
                            html.Div([
                                html.P(children='Intervalo de previsão padrão (min)'
                                       ,style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px', 'text-align': 'center'}),
                                dcc.Input(id='input-intervalo_padrao',type='text', value=configs['intervalo_padrao'][0]
                                          ,style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px', 'text-align': 'center'}),
                                dbc.Switch(id='input-grafico_barras', label='Mostrar gráfico de barras', value=configs['grafico_barras'][0]),
                                dbc.Switch(id='input-previsao_home', label='Mostrar previsão padrão', value=configs['previsao_home'][0]),
                                html.P(children='Estoque mínimo (%)',style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px', 'text-align': 'center'}),
                                dcc.Input(id='input-estoque_minimo',type='text', value=configs['estoque_minimo'][0],style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'marginBottom': '20px', 'text-align': 'center'}),
                                html.Button('Salvar', id='botao-salvar_config', style={'width': '150px', 'height': '50px', 'font-size': '25px'}),
                            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'margin-bottom': "25px"}),
                            ]),
        return layout2
    else:
        return html.Div('Página Inexistente')
    
def adjust_forecast_index(df_forecast, n_steps, df_real):
    last_date = df_real.index[-1] + timedelta(minutes=5)
    forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='5min')
    df_forecast.index = forecast_dates
    return df_forecast
    
def forecast_holt(df_holt, n_steps, periods=40):
    model = ExponentialSmoothing(endog=df_holt, trend='add', seasonal='add', seasonal_periods=periods, freq="5min").fit(optimized=True)

    forecasting_hw = model.forecast(steps = n_steps)
    
    forecasting_hw = adjust_forecast_index(forecasting_hw, n_steps, df_holt)
    
    forecasting_hw = pd.concat([df_holt.iloc[[len(df_holt)-1]], forecasting_hw])
    
    forecasting_hw[forecasting_hw < 0] = 0
    
    return forecasting_hw
    
def forecast_arima(df_arima, n_steps, periods=1):
    model = auto_arima(y=df_arima, m=periods)

    forecasting_arima = pd.Series(model.predict(n_periods=n_steps))

    forecasting_arima = adjust_forecast_index(forecasting_arima, n_steps, df_arima)
    
    forecasting_arima = pd.concat([df_arima.iloc[[len(df_arima)-1]], forecasting_arima])
    
    forecasting_arima[forecasting_arima < 0] = 0
    
    return forecasting_arima

def cortar_df(df_historico, intervalo, mult):
    data_final = df_historico.index[-1]
    data_inicial = data_final - timedelta(minutes=mult*intervalo)
    data_inicial = pd.to_datetime(data_inicial)
    
    df_cortado = df_historico[df_historico.index >= data_inicial]
    
    return df_cortado

def df_to_series(df_historico):
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    return df_historico

def transformar_series_para_decrescente(series):
    nova_serie = pd.DataFrame(columns=['quant', 'data'])
    flag = False
    acumulado = 0
    for i in range(len(series)-1, -1, -1):
        valor = series.iloc[i]
        if i < len(series)-1 and series.iloc[i] < series.iloc[i+1]:
            acumulado += 500
            flag = True
        if flag == True:
            valor = series.iloc[i] + acumulado
        nova_serie.loc[len(nova_serie)] = {"data": series.index[i], "quant": valor}
    nova_serie = df_to_series(nova_serie)
    nova_serie = nova_serie.iloc[::-1]
    return nova_serie

def obter_df_historico(id_produto):
    df_historico = historico(id_produto)
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    df_historico = ajustar_df(df_historico)
    df_grafico = df_historico
    
    df_historico = transformar_series_para_decrescente(df_grafico)
    df_historico = ajustar_df(df_historico)
    
    return df_historico, df_grafico

def ajustar_df(df_historico):
    df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]

    df_ajustado = df_ajustado.resample('5min')
    df_ajustado = df_ajustado.ffill().bfill()
    df_ajustado = df_ajustado.interpolate(method='linear')
    
    return df_ajustado

def create_forecast_graph(df_real, df_previsto, title):
    return html.Div([
        dcc.Graph(id={'type': 'product-figures', 'index': 1},figure={
            'data': [
                go.Scatter(
                    x=df_real.index,
                    y=df_real,
                    mode='lines',
                    name='Dados reais',
                    line=dict(color='blue')
                ),
                go.Scatter(
                    x=df_previsto.index,
                    y=df_previsto,
                    mode='lines',
                    name='Dados previstos',
                    line=dict(color='red')
                )
            ],
            'layout': go.Layout(
                title={'text': title, 'font': {'size': 24}},
                xaxis={'title': 'Tempo', 'titlefont': {'size': 18}},
                yaxis={'title': 'Quantidade de Produtos nas Prateleiras', 'titlefont': {'size': 18}},
                legend=dict(
                    orientation="h",
                    x=0,
                    y=-0.25,
                    xanchor='left',
                    yanchor='top'
                ),
                margin=dict(
                    l=60, r=20, t=40, b=40
                ),
                modebar= {
                    "orientation": 'v',
                },
            )
        })
    ], className="col-12 col-md-6")

#------------------------------------------------------ Salvar configurações ----------------------------------------------------------------#
@callback(
    Input('botao-salvar_config', 'n_clicks'), 
    State('input-intervalo_padrao', 'value'),
    State('input-grafico_barras', 'value'),
    State('input-previsao_home', 'value'),
    State('input-estoque_minimo', 'value')
)
def criar_forecast_graph(n_clicks, intervalo_padrao, grafico_barras, previsao_home, estoque_minimo):
    saveConfig(intervalo_padrao, grafico_barras, previsao_home, estoque_minimo)
    return

#------------------------------------------------------ Botão previsão ----------------------------------------------------------------#
@callback(
    Output('graphs-container-previsao', 'children'),
    Input('botao-prever', 'n_clicks'), 
    State('input-intervalo', 'value'),
    State('dropdown-produto-prever', 'value')
)
def criar_forecast_graph(n_clicks, intervalo, id_produto):
    if not(id_produto): return
    
    n_steps = int(int(intervalo)/5) + 1
    
    df_historico, df_grafico = obter_df_historico(id_produto)

    df_cortado = cortar_df(df_grafico, n_steps, 10)
    
    df_arima = forecast_arima(df_historico, n_steps, 1)
    
    df_holt = forecast_holt(df_historico, n_steps, 2)
    
    graph_div_holt = create_forecast_graph(df_cortado, df_holt, "Previsão com Holt Winter")
    
    graph_div_arima = create_forecast_graph(df_cortado, df_arima, "Previsão com Arima")
    
    graph_div = [graph_div_holt, graph_div_arima]

    return graph_div
    
# ------------------------------------------------------ Dialog ----------------------------------------------------------------#
@callback(
    Output("modal", "is_open"),
    [Input("botao-add-produtos", "n_clicks"), Input("botao-criar", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return is_open
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "botao-add-produtos" and not is_open:
        return True
    elif button_id == "botao-criar" and is_open:
        return False
    
    return is_open
    
# ------------------------------------------------------ Gráfico de barras ----------------------------------------------------------------#

@callback(
    Output('bar-graph', 'figure'),
    Output('bar-graph', 'style'),
    [Input('interval-component', 'n_intervals')],
    [State('dropdown-values', 'data')],
)
def update_bar_chart(n_intervals, dropdown_values):
    if dropdown_values is None or dropdown_values == []:
        return go.Figure(), {'display': 'none'}
    df_bar_teste = df_bar[df_bar['id_produto'].isin(dropdown_values)]
    teste = produtos[produtos['id_produto'].isin(dropdown_values)]
    
    df_merged = pd.merge(df_bar_teste, teste, on='id_produto')
    df_merged['nome_produto']
    
    fig = px.bar(df_merged,
        x='nome_produto',
        y='quant_total',
        labels={"nome_produto": "Produto", "quant_total": "Quantidade"},
        color='nome_produto',
    )
    
    fig.update_layout(
        showlegend=False, 
        title={'text': "Vendas de produtos", 'x': 0.5, 'xanchor': 'center', 'font': {'size': 24}},
        xaxis={'title': 'Produto','tickfont': {'size': 18}, 'titlefont': {'size': 18}},
        yaxis={'title': 'Quantidade vendida', 'titlefont': {'size': 18}},
        modebar= {
            "orientation": 'v',
        },
        uirevision='some-constant', 
        )
    
    return fig, {'display': 'block'}

# --------------------------------------------------------------------------------------------------------------------------------------------#
def criar_threads_produto():
    global produtos
    global df
    
    produtos = obterProdutos()
    df = select()
    
    quant_estoque = obterEstoqueAtual()

    queue = Queue()
    produto = ""
    thread = ""
    
    produto = Thread(target=comprarProduto, args=(queue, produtos["id_produto"].iloc[-1], ))
    produto.start()
    
    thread = Thread(target=generate_random_numbers, args=(queue, quant_estoque[-1], produtos["id_produto"].iloc[-1] ))
    thread.start()

#------------------------------------------------------ Criação de Produto ----------------------------------------------------------------#
@callback(
    Output('dropdown-values', 'data'),
    Input("modal", "is_open"),
    State('dropdown-produto', 'value'),
)
def adicionar_grafico(n_clicks, selected_items):
    global selected_itemsGeral
    if selected_items is None or len(selected_items) == 0:
        return []
    if selected_items and 'ALL' in selected_items:
        selected_itemsGeral = [opt['value'] for opt in get_options_from_db() if opt['value'] != 'ALL']
        return selected_itemsGeral
    else:
        selected_itemsGeral = selected_items
        return selected_itemsGeral
        
@callback(
    Output('dropdown-produto', 'value'),
    [Input('dropdown-values', 'data')], 
)
def adicionar_grafico(dropdown_values):
    return dropdown_values

#------------------------------------------------------ Criação Gráficos ----------------------------------------------------------------#
@callback(
    Output('graphs-container', 'children'),
    Input('dropdown-produto', 'value'),
    [State('dropdown-values', 'data')],
)
def update_layout(n, dropdown_values):
    graphs = []
    produtos = dropdown_values
    if not(produtos): produtos = []

    for i in produtos:
        graph_div = html.Div([
            dcc.Graph(id={'type': 'product-figures', 'index': i},)
        ], className="col-12 col-md-6")

        graphs.append(graph_div)

    return graphs

#------------------------------------------------------ Atualização Gráficos ----------------------------------------------------------------#
@callback(
    Output({"type": "product-figures", "index": ALL}, "figure"),
    [Input('interval-component', 'n_intervals')],
    [State('dropdown-values', 'data')]
)
def update_graphs(n, dropdown_values):
    
    global df
    dff = df
    
    graficos = []
    
    global produtos

    produtos_selecionados = produtos[produtos['id_produto'].isin(dropdown_values)]
    
    for indice, linha in produtos_selecionados.iterrows():
        id = linha.id_produto
        name = linha.nome_produto
        graficos.append(GraficoProduto(go.Figure(data=go.Scatter(x=dff['data'].loc[dff['id_produto'] == id], y=dff['quant'].loc[dff['id_produto'] == id], mode="lines")),id,name))
    
    for fig in graficos:
            fig.grafico.update_layout(
                uirevision='some-constant', 
                showlegend=False, 
                xaxis_autorange=True, 
                yaxis_autorange=True, 
                autosize=True, 
                title={'text': 'Monitoramento de consumo de ' + fig.name, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 22}},
                xaxis={'title': 'Tempo', 'titlefont': {'size': 18}},
                yaxis={'title': 'Quantidade de Produtos nas Prateleiras', 'titlefont': {'size': 18}},
                modebar= {
                    "orientation": 'v',
                },
                margin=dict(l=20, r=20, t=40, b=40),
            )
    
    return [graficos[i].grafico for i in range(len(graficos))]

#------------------------------------------------------ Ranking ----------------------------------------------------------------#

@callback(
    [Input('interval-previsao', 'n_intervals')],
    [State('dropdown-values', 'data')]
)
def getRanking(n, dropdown_values):
    global df
    if dropdown_values == None or dropdown_values == []:
        return None
    thread = Thread(target=ranquamento, args=(df, dropdown_values))
    thread.start()


@callback(
    Output('ranking-values', 'data'), 
    [Input('interval-check', 'n_intervals')],
)
def getRanking(n):
    global store
    if store:
        return store
    else:
        return False

def ranquamento(df, dropdown_values):
    global store
    
    configs = obter_config()
    intervalo = configs['intervalo_padrao'][0]
    estoque_minimo = configs['estoque_minimo'][0]
    
    previsoes = pd.DataFrame(columns=['id_produto', 'quant'])
    
    produtos_selecionados = produtos[produtos['id_produto'].isin(dropdown_values)]
    
    for id_produto in produtos_selecionados['id_produto']:
        df_historico, _ = obter_df_historico(id_produto)
        
        df_arima = forecast_arima(df_historico, int(intervalo))
        
        df_arima = df_arima.iloc[len(df_arima)-1]
        
        percentage = (100*df_arima)/produtos.loc[produtos['id_produto'] == id_produto]['quant_max_prateleira'].values[0]
        
        if percentage < estoque_minimo:
            new_row = {'id_produto': id_produto, 'quant': percentage}
            previsoes.loc[len(previsoes)] = new_row
    
    ranking = previsoes.groupby('id_produto').last().reset_index().sort_values(by='quant', ascending=True)['id_produto']
    df_merged = pd.merge(ranking, produtos_selecionados, on='id_produto')
    store['result'] = df_merged['nome_produto']
    return

@callback(
    Output('dynamic-content', 'children'),
    Input('ranking-values', 'data'),
    State('dynamic-content', 'children'),
    [State('dropdown-values', 'data')]
)
def adicionar_grafico(data, antigo, dropdown_values):
    if dropdown_values == None: return
    produtos_selecionados = produtos[produtos['id_produto'].isin(dropdown_values)]
    if data['result'] and (not produtos_selecionados.empty):
        ranking = data.get('result')
        return [html.P("Previsão Padrão de Reabastecimento", style={'textAlign':'center', 'font-size': "24px"})] + [html.P(produto, style={'textAlign':'center', 'font-size': "18px"}) for produto in ranking]
    return [html.P("", style={'textAlign':'center'})]

if __name__ == "__main__":
    main()