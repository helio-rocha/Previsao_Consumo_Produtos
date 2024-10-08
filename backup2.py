from queue import Queue
from threading import Thread, Event, Lock
import threading
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from datetime import datetime
import mysql.connector
import sqlalchemy
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from grafico_produto import GraficoProduto

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

produtos = pd.DataFrame(columns=['ID', 'nome_produto'])
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
        quant_estoque = [df['quant'].iloc[-1], df['quant'].iloc[-1], df['quant'].iloc[-1], df['quant'].iloc[-1]]
    except:
        quant_estoque = [200, 200, 200, 200]
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

def main(): 
    quant_estoque = obterEstoqueAtual()
    
    # Fila
    queue = [Queue(), Queue(), Queue(), Queue()]
    produto = ["","","",""]
    thread = ["","","",""]
    
    for i in range(1, 5):
        produto[i-1] = Thread(target=comprarProduto, args=(queue[i-1], i, ))
        produto[i-1].start()
        
        thread[i-1] = Thread(target=generate_random_numbers, args=(queue[i-1], df, quant_estoque[i-1], i ))
        thread[i-1].start()
        
    app = Dash(suppress_callback_exceptions=True, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'])

    app.layout =  html.Div([
        dcc.Location(id='url', refresh=False),
        html.Button('Ir para Page 2', id='meu-botao'),  # O botão que desencadeará o evento
        html.Div(id='page-content'),
    ])
        
    app.run(debug=True, use_reloader=False)
    
@callback(
    Output('url', 'pathname'),  # O output vai alte rar o pathname da URL
    Input('meu-botao', 'n_clicks'),  # O input é o número de cliques no botão
    Input('url', 'pathname'),  # O input que captura o pathname atual
)
def redirecionar_page2(n_clicks, pathname):
    if n_clicks:  # Verifica se o botão foi clicado
        return '/page-2'  # Redireciona para page-2
    return pathname  # Mantém na página inicial se o botão não foi clicado

@callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-1':
        layout = html.Div([html.H1(children='Monitoramento de estoque', style={'textAlign':'center'}),
    html.Div(id='plots', style={'textAlign':'center'}),
        html.Div(dcc.Graph(id='scatter-plot-3'), className="col-12 col-md-6"),  # Coluna 3
        html.Div(dcc.Graph(id='scatter-plot-3'), className="col-12 col-md-6"),  # Coluna 3
    
        html.Div(dcc.Graph(id='scatter-plot-3'), className="col-12 col-md-6"),  # Coluna 3
    
    html.P("Ranking", style={'textAlign':'center'}),
    html.Div(id='dynamic-content', style={'textAlign':'center'}),
        dcc.Interval(
            id='interval-component',
            interval=10000,
            n_intervals=0,
        ),])
        return layout
    elif pathname == '/page-2':
        return html.Div('Você está na Página 2')
    else:
        return html.Div('Página inicial')

@callback(
    [Output('plots', 'children'),
     Output('dynamic-content', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    
    fig = make_subplots(rows=2, cols=2)
    
    dff = df
    
    graficos = []
    
    for indice, linha in produtos.iterrows():
        id = linha.id_produto
        name = linha.nome_produto
        graficos.append(GraficoProduto(go.Figure(data=go.Scatter(x=dff['data'].loc[dff['id_produto'] == id], y=dff['quant'].loc[dff['id_produto'] == id], mode="lines")),id,name))

    
    for fig in graficos:
            fig.grafico.update_layout(uirevision='some-constant', showlegend=False, xaxis_autorange=True, yaxis_autorange=True, autosize=True, title=fig.name)
            
    ranking = ranquamento(df)
    
    for elemento in graficos:
        print(elemento.grafico)

    # Retorna os gráficos individualmente para cada Output
    return [html.Div(dcc.Graph((elemento.grafico))) for elemento in graficos], [html.P(teste) for teste in ranking]

def ranquamento(df):
    ranking = df.groupby('id_produto').last().reset_index().sort_values(by='quant', ascending=True)['id_produto']#.astype(str).tolist()
    # print(ranking)
    df_merged = pd.merge(ranking, produtos, on='id_produto')
    return df_merged['nome_produto']


if __name__ == "__main__":
    main()