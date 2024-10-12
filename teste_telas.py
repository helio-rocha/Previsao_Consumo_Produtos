from queue import Queue
from threading import Thread, Event, Lock
import threading
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
from datetime import datetime
import mysql.connector
import sqlalchemy
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from grafico_produto import GraficoProduto
import dash

lock = Lock()

# Credenciais de acesso ao banco de dados
host = "localhost"
user = "root"
password = "root"
database = "supermercado"

def select():
    # connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT horario AS data, quantidade_estoque AS quant, id_produto FROM consumo_produtos ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

def obterProdutos():
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT ID AS id_produto, nome_produto FROM produtos ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

df = pd.DataFrame(columns=['quant', 'data', 'id_produto'])
df = select()

produtos = pd.DataFrame(columns=['id_produto', 'nome_produto'])
produtos = obterProdutos()

def comprarProduto(queue, id_produto):
    while True:
        tempo = geracaoTempo()
        quant = geracaoQuant()
        time.sleep(tempo)
        date = gerarData()
        data = {"quant": quant, "data": date}
        queue.put(data)

def obterEstoqueAtual():
    try:
        quant_estoque = [df['quant'].iloc[-1] for i in range(len(produtos))]
    except:
        quant_estoque = [200 for i in range(len(produtos))]
    return quant_estoque

def gerarData():
    date = datetime.now()
    dt_string = date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return dt_string


def saveDB(quant, date, quant_estoque, id_produto):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        # print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO consumo_produtos (horario, id_produto, quantidade_comprada, quantidade_estoque) VALUES ('{date}', {id_produto}, {quant}, {quant_estoque});"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
                # print("Conexão fechada")
        except:
            pass

def geracaoTempo():
    return random.expovariate(1)
    
def geracaoQuant():
    quant = random.randint(1, 5)
    return quant

def generate_random_numbers(queue, dff, quant_estoque, id_produto):
    # print("Inciou")
    while quant_estoque > 0:
        # with lock:
            data = queue.get()
            quant = data['quant']
            date = data['data']
            quant_estoque = quant_estoque - quant
            if quant_estoque < 0:
                quant = quant + quant_estoque
                quant_estoque = 0
            new_row = {'quant': quant_estoque, 'data': date, 'id_produto': id_produto}
            dff.loc[len(dff)] = new_row
            saveDB(quant, date, quant_estoque, id_produto)
            # print(f"Quant {quant}. Quant_Estoque {quant_estoque}  Data {date} id_produto {id_produto}")
            if quant_estoque == 0:
                quant_estoque = 200
                
app = Dash(suppress_callback_exceptions=True, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

default_layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='url2', refresh=False),
        html.Button('Home', id='botao-home'),  # O botão que desencadeará o evento
        html.Button('Adicionar Produtos', id='botao-add-produtos'),  # O botão que desencadeará o evento
        html.Button('Previsão', id='botao-previsao'),  # O botão que desencadeará o evento
        html.Button('Configurações', id='botao-config'),  # O botão que desencadeará o evento
        html.Div(id='page-content'),
    ])

def main(): 
    quant_estoque = obterEstoqueAtual()
    
    # Fila
    queue = [Queue() for i in range(len(produtos))]
    produto = ["" for i in range(len(produtos))]
    thread = ["" for i in range(len(produtos))]
    
    for i in range(len(produtos)):
        produto[i] = Thread(target=comprarProduto, args=(queue[i], produtos["id_produto"].loc[i], ))
        produto[i].start()
        
        thread[i] = Thread(target=generate_random_numbers, args=(queue[i], df, quant_estoque[i], produtos["id_produto"].loc[i] ))
        thread[i].start()

    app.layout = default_layout
        
    app.run(debug=True, use_reloader=False)
    
@callback(
    Output('url', 'pathname'),  # O output vai alte rar o pathname da URL
    [Input('botao-home', 'n_clicks'),
     Input('botao-add-produtos', 'n_clicks'),
     Input('botao-previsao', 'n_clicks'),
     Input('botao-config', 'n_clicks'),
     ],
    Input('url', 'pathname'),  # O input que captura o pathname atual
)
def redirecionar_page(n1, n2, n3, n4, pathname):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    # Identifica qual botão foi clicado
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'botao-home' and n1:
        return '/home'
    elif button_id == 'botao-add-produtos' and n2:
        return '/add_produto'
    elif button_id == 'botao-previsao' and n3:
        return '/previsao'
    elif button_id == 'botao-config' and n3:
        return '/config'

    return pathname

#------------------------------------------------------ Páginas ----------------------------------------------------------------#

@callback(Output('page-content', 'children'),
            Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/home':
        layout = html.Div([html.H1(children='Monitoramento de estoque', style={'textAlign':'center'}),
                            dcc.Store(id='data-store'),  
                            html.Div(id='graphs-container', style={'display': 'flex', 'flex-wrap': 'wrap'}),
                            dcc.Interval(
                                id='interval-component',
                                interval=10000,
                                n_intervals=0,
                            ),
                            html.P("Ranking", style={'textAlign':'center'}),
                            html.Div(id='dynamic-content', style={'textAlign':'center'})
                            ]),
        return layout
    elif pathname == '/add_produto':
        layout2 = html.Div([html.H1(children='Adicionar produtos', style={'textAlign':'center'}),
                            dcc.Input(id='input-nome-produto',type='text', value=''),
                            dcc.Input(id='input-teste',type='text', value=''),
                            html.Button('Criar', id='botao-criar'),  # O botão que desencadeará o evento
                            ]),
        return layout2
    elif pathname == '/previsao':
        layout2 = html.Div([html.H1(children='Previsão', style={'textAlign':'center'})]),
        return layout2
    elif pathname == '/config':
        layout2 = html.Div([html.H1(children='Config', style={'textAlign':'center'}),]),
        return layout2
    else:
        return html.Div('Página inicial')
    
def criar_produto(nome):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        # print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO produtos (nome_produto) VALUES ('{nome}');"
        cursor.execute(consulta)
        
        connection.commit()
            
    except mysql.connector.Error as err:
        print("Erro na conexão: {}".format(err))
    finally:
        try:
            if connection:
                connection.close()
                # print("Conexão fechada")
        except:
            pass
        
def criar_threads_produto():
    quant_estoque = obterEstoqueAtual()
    # Fila
    queue = Queue()
    produto = ""
    thread = ""
    
    produto = Thread(target=comprarProduto, args=(queue, produtos["id_produto"].iloc[-1], ))
    produto.start()
    
    thread = Thread(target=generate_random_numbers, args=(queue, df, quant_estoque[-1], produtos["id_produto"].iloc[-1] ))
    thread.start()

#------------------------------------------------------ Criação de Produto ----------------------------------------------------------------#
@callback(
    Input('botao-criar', 'n_clicks'), 
    State('input-nome-produto', 'value'),  # Captura o valor atual do input1
    State('input-teste', 'value')   # Captura o valor atual do input2
)
def atualizar_texto_html(n_clicks, nome_produto, teste):
    criar_produto(nome_produto)
    global produtos
    global df
    print(produtos)
    produtos = obterProdutos()
    print(produtos)
    df = select()
    criar_threads_produto()
    generate_update()

#------------------------------------------------------ Criação Gráficos ----------------------------------------------------------------#
@callback(
    Output('graphs-container', 'children'),
    [Input('data-store', 'data')]
)
def update_layout(n):
    graphs = []
    produtos = obterProdutos()

    for i, produto in enumerate(produtos['nome_produto']):
        # Adiciona um título e um gráfico para cada produto
        graph_div = html.Div([
            dcc.Graph(id=f'graph-{i}')
        ], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'})  # Controla o tamanho de cada gráfico e espaço

        graphs.append(graph_div)

    return graphs

#------------------------------------------------------ Atualização Gráficos ----------------------------------------------------------------#

def generate_update():
        # Remove o callback existente para gráficos
    # print(app.callback_map)
    if 'update_graphs' in app.callback_map:
        print("asfasfasfasfafafaafasf")
        del app.callback_map['update_graphs']
    print(app.callback_map)
        
    # # Callback para atualizar cada gráfico com base nos produtos
    # @callback(
    #     [Output(f'graph-{i}', 'figure') for i in range(len(produtos))],
    #     [Input('interval-component', 'n_intervals')]
    # )
    # def update_graphs(n):
        
    #     dff = df
        
    #     print(len(produtos))
        
    #     graficos = []
        
    #     for indice, linha in produtos.iterrows():
    #         id = linha.id_produto
    #         name = linha.nome_produto
    #         graficos.append(GraficoProduto(go.Figure(data=go.Scatter(x=dff['data'].loc[dff['id_produto'] == id], y=dff['quant'].loc[dff['id_produto'] == id], mode="lines")),id,name))

        
    #     for fig in graficos:
    #             fig.grafico.update_layout(uirevision='some-constant', showlegend=False, xaxis_autorange=True, yaxis_autorange=True, autosize=True, title=fig.name)
        
    #     return [graficos[i].grafico for i in range(len(graficos))]

# Callback para atualizar cada gráfico com base nos produtos
@callback(
    [Output(f'graph-{i}', 'figure') for i in range(len(produtos))],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    
    dff = df
    
    print(len(produtos))
    
    graficos = []
    
    for indice, linha in produtos.iterrows():
        id = linha.id_produto
        name = linha.nome_produto
        graficos.append(GraficoProduto(go.Figure(data=go.Scatter(x=dff['data'].loc[dff['id_produto'] == id], y=dff['quant'].loc[dff['id_produto'] == id], mode="lines")),id,name))

    
    for fig in graficos:
            fig.grafico.update_layout(uirevision='some-constant', showlegend=False, xaxis_autorange=True, yaxis_autorange=True, autosize=True, title=fig.name)
    
    return [graficos[i].grafico for i in range(len(graficos))]

#------------------------------------------------------ Ranking ----------------------------------------------------------------#

@callback(
    Output('dynamic-content', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    
    ranking = ranquamento(df)

    # Retorna os gráficos individualmente para cada Output
    return [html.P(teste) for teste in ranking]

def ranquamento(df):
    ranking = df.groupby('id_produto').last().reset_index().sort_values(by='quant', ascending=True)['id_produto']#.astype(str).tolist()
    df_merged = pd.merge(ranking, produtos, on='id_produto')
    return df_merged['nome_produto']


if __name__ == "__main__":
    main()