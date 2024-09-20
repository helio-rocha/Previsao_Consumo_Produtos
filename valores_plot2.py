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

lock = Lock()

# Credenciais de acesso ao banco de dados
host = "localhost"
user = "root"
password = "root"
database = "supermercado"

def select():
    # connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    engine = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/supermercado')
    query = "SELECT horario AS data, quantidade_estoque AS quant FROM consumo_produtos ORDER BY ID ASC"
    df = pd.read_sql(query, con = engine)
    return df

df = pd.DataFrame(columns=['quant', 'data'])
df = select()

def comprarProduto(queue):
    while True:
        tempo = geracaoTempo()
        quant = geracaoQuant()
        time.sleep(tempo)
        date = gerarData()
        data = {"quant": quant, "data": date}
        queue.put(data)

def obterEstoqueAtual():
    try:
        quant_estoque = df['quant'].iloc[-1]
    except:
        quant_estoque = 200
    return quant_estoque

def gerarData():
    date = datetime.now()
    dt_string = date.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    return dt_string


def saveDB(quant, date, quant_estoque):
    try:
        connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        print("Conectado ao banco de dados MySQL!")
        
        # Criando um cursor para executar consultas
        cursor = connection.cursor()
        
        consulta = f"INSERT INTO consumo_produtos (horario, quantidade_comprada, quantidade_estoque) VALUES ('{date}', {quant}, {quant_estoque});"
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

def generate_random_numbers(queue, dff, quant_estoque):
    print("Inciou")
    while quant_estoque > 0:
        with lock:
            data = queue.get()
            quant = data['quant']
            date = data['data']
            quant_estoque = quant_estoque - quant
            if quant_estoque < 0:
                quant = quant + quant_estoque
                quant_estoque = 0
            new_row = {'quant': quant_estoque, 'data': date}
            dff.loc[len(dff)] = new_row
            saveDB(quant, date, quant_estoque)
            print(f"Quant {quant}. Quant_Estoque {quant_estoque}  Data {date}")
            if quant_estoque == 0:
                quant_estoque = 200

def main(): 
    quant_estoque = obterEstoqueAtual()
    
    # Fila
    queue = Queue()
    
    produto = Thread(target=comprarProduto, args=(queue, ))
    produto.start()
    
    thread = Thread(target=generate_random_numbers, args=(queue, df, quant_estoque, ))
    thread.start()
        
    app = Dash()

    app.layout = [
        html.H1(children='Monitoramento de estoque', style={'textAlign':'center'}),
        dcc.Graph(id='graph-content'),
        dcc.Interval(
            id='interval-component',
            interval=1*500,
            n_intervals=0
        )
    ]
    
    app.run(debug=True, use_reloader=False)


@callback(
    Output('graph-content', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    
    fig = px.line(df, x='data', y='quant')
    
    fig.update_layout(uirevision='some-constant')
    
    return fig


if __name__ == "__main__":
    main()
