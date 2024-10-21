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

df = pd.DataFrame(columns=['quant', 'data', 'id_produto'])
df = select()

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
        print("Conectado ao banco de dados MySQL!")
        
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
                print("Conexão fechada")
        except:
            pass

def geracaoTempo():
    return random.expovariate(1)
    
def geracaoQuant():
    quant = random.randint(1, 5)
    return quant

def generate_random_numbers(queue, dff, quant_estoque, id_produto):
    print("Inciou")
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
            print(f"Quant {quant}. Quant_Estoque {quant_estoque}  Data {date} id_produto {id_produto}")
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
        
    app = Dash()

    app.layout =  html.Div([
        html.H1(children='Monitoramento de estoque', style={'textAlign':'center'}),
        dcc.Graph(id='scatter-plot'),
        dcc.Interval(
            id='interval-component',
            interval=500,
            n_intervals=0
        ),
    ])
        
    app.run(debug=True, use_reloader=False)


@callback(
    Output('scatter-plot', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    
    fig = make_subplots(rows=2, cols=2)
    
    dff = df
    
    print("")
    
    # grafico1 = px.line(df, x='data', y='quant')
    grafico1 = go.Scatter(x=dff['data'].loc[dff['id_produto'] == 1], y=dff['quant'].loc[dff['id_produto'] == 1], mode="lines")
    grafico2 = go.Scatter(x=dff['data'].loc[dff['id_produto'] == 2], y=dff['quant'].loc[dff['id_produto'] == 2], mode="lines")
    grafico3 = go.Scatter(x=dff['data'].loc[dff['id_produto'] == 3], y=dff['quant'].loc[dff['id_produto'] == 3], mode="lines")
    grafico4 = go.Scatter(x=dff['data'].loc[dff['id_produto'] == 4], y=dff['quant'].loc[dff['id_produto'] == 4], mode="lines")
    # grafico2 = go.scatter(df, x='data', y='quant', mode="lines")
    # grafico2 = px.line(df, x='data', y='quant')
    
    fig.add_trace(grafico1, row=1, col=1)
    fig.add_trace(grafico2, row=1, col=2)
    fig.add_trace(grafico3, row=2, col=1)
    fig.add_trace(grafico4, row=2, col=2)
    
    fig.update_layout(uirevision='some-constant', height=800, showlegend=False)
    
    return fig


if __name__ == "__main__":
    main()
