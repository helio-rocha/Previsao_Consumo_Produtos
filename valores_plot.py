from queue import Queue
from threading import Thread, Event, Lock
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
    query = "SELECT horario AS data, quantidade_estoque AS quant FROM consumo_produtos"
    df = pd.read_sql(query, con = engine)
    return df

df = pd.DataFrame(columns=['quant', 'data'])
df = select()
flag = True

def comprarProduto():
    tempo = geracaoTempo()
    quant = geracaoQuant()
    time.sleep(tempo)
    date = gerarData()
    # if flag:
    try:
        # flag = False
        quant_estoque = df['quant'].iloc[-1]
    except:
        quant_estoque = 1000
    quant_estoque = quant_estoque - quant
    saveDB(quant, date, quant_estoque)
    data = {"quant": quant, "data": date}
    return data

def gerarData():
    date = datetime.now()
    dt_string = date.strftime("%Y-%m-%d %H:%M:%S")
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

def generate_random_numbers(dff):
    quant_prod = 1000
    while quant_prod > 0:
        data = comprarProduto()
        quant_prod = quant_prod - data['quant']
        with lock:
            new_row = {'quant': quant_prod, 'data': data['data']}
            dff.loc[len(dff)] = new_row
            print(f"Quant {data['quant']}. Data {data['data']}")

def main():    
    print(df)
    
    thread = Thread(target=generate_random_numbers, args=(df, ))
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
    
    app.run(debug=True)


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
