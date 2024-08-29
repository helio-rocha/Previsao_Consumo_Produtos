from queue import Queue
from threading import Thread, Event, Lock
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

hist = []

# Evento de controle
stop_event = Event()

lock = Lock()

df = pd.DataFrame(columns=['quant', 'tempo'])



def comprarProduto(lambT, lambQ):
    # data = []
    # while not stop_event.is_set():
    tempo = geracaoTempo(lambT)
    quant = geracaoQuant(lambQ)
    data = {"quant": quant, "tempo": tempo}
    # time.sleep(tempo)
    return data
    # print(data)
    # queue.put(data)

def geracaoTempo(lamb):
    return random.expovariate(lamb)
    
def geracaoQuant(lamb):
    quant = random.expovariate(lamb)
    quant = round(quant) + 1
    if quant < 1: quant = 1
    return quant

def generate_random_numbers(dff):
    tempo_total = 0
    quant_prod = 100
    while quant_prod > 0:
        data = comprarProduto(1, 1)
        data['tempo'] = tempo_total + data['tempo']
        tempo_total = data['tempo']
        quant_prod = quant_prod - data['quant']
        with lock:
            new_row = {'quant': quant_prod, 'tempo': data['tempo']}
            dff.loc[len(dff)] = new_row
            print(f"Thread {data['quant']} added {data['tempo']}")
        # time.sleep(1)

def main():
    # Parâmetros das variáveis aleatórias geradas
    lambT = 1
    lambQ = 1
    
    # Quantidade inicial de produtos
    # quantidade_produtos = 1000
    
    # Fila
    # queue = Queue()
    
    # Threads
    # produto = Thread(target=comprarProduto, args=(queue, lambT, lambQ))
    # comprar = Thread(target=simular_compra, args=(queue, quantidade_produtos))
    
    # Inicia
    # produto.start()
    # comprar.start()
    
    # Parar 
    # comprar.join()
    # produto.join()
    
    thread = Thread(target=generate_random_numbers, args=(df,))
    thread.start()
        
    app = Dash()

    app.layout = [
        html.H1(children='Title of Dash App', style={'textAlign':'center'}),
        # dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
        dcc.Graph(id='graph-content'),
        dcc.Interval(
            id='interval-component',
            interval=1*500, # in milliseconds
            n_intervals=0
        )
    ]
    
    app.run(debug=True)
    
    # try:
    #     while True:
    #         with lock:
    #             print(df)
    #         time.sleep(5)
    # except KeyboardInterrupt:
    #     print("Stopping the monitoring.")


@callback(
    Output('graph-content', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    return px.line(df, x='tempo', y='quant')


if __name__ == "__main__":
    main()
