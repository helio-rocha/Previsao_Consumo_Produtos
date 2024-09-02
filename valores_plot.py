from queue import Queue
from threading import Thread, Event, Lock
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

hist = []

lock = Lock()

df = pd.DataFrame(columns=['quant', 'tempo'])

def comprarProduto():
    tempo = geracaoTempo()
    quant = geracaoQuant()
    data = {"quant": quant, "tempo": tempo}
    time.sleep(tempo)
    return data

def geracaoTempo():
    return random.expovariate(1)
    # return random.normalvariate(1, 2)
    
def geracaoQuant():
    lamb = 1
    quant = random.expovariate(lamb)
    quant = round(quant) + 1
    if quant < 1: quant = 1
    return quant

def generate_random_numbers(dff):
    tempo_total = 0
    quant_prod = 1000
    while quant_prod > 0:
        data = comprarProduto()
        data['tempo'] = tempo_total + data['tempo']
        tempo_total = data['tempo']
        quant_prod = quant_prod - data['quant']
        with lock:
            new_row = {'quant': quant_prod, 'tempo': data['tempo']}
            dff.loc[len(dff)] = new_row
            print(f"Quant {data['quant']}. Tempo {data['tempo']}")

def main():
    
    thread = Thread(target=generate_random_numbers, args=(df, ))
    thread.start()
        
    app = Dash()

    app.layout = [
        html.H1(children='Compra de produtos', style={'textAlign':'center'}),
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
    
    fig = px.line(df, x='tempo', y='quant')
    
    fig.update_layout(uirevision='some-constant')
    
    return fig


if __name__ == "__main__":
    main()
