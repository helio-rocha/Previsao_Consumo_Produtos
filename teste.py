from queue import Queue
from threading import Thread, Event, Lock
import threading
import random
import numpy as np
import time
from dash import Dash, html, dcc, callback, Output, Input, State, ALL, Patch
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
import mysql.connector
import sqlalchemy
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from grafico_produto import GraficoProduto
import dash
from database import select, obterProdutos, obterVendas, saveDB, get_options_from_db, criar_produto

app = Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

default_layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='url2', refresh=False),
        dcc.Store(id='dropdown-values'),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Título do Dialog")),
                dbc.ModalBody("Este é o conteúdo do seu dialog."),
                dbc.ModalFooter(
                    dbc.Button("Fechar", id="close-modal", className="ml-auto", n_clicks=0)
                ),
            ],
            id="modal",
            is_open=False,
            size="lg",  # Definido para grande, pode ser "sm", "lg" ou "xl"
            backdrop=True,  # Permite fechar ao clicar fora do modal
            keyboard=True,  # Permite fechar ao pressionar "ESC"
            centered=True,  # Centralizado na tela
        ),
        html.Div([
                html.Button(html.Span("home", className="material-icons"), id='botao-home',),  # O botão que desencadeará o evento
                html.Button(html.Span("add", className="material-icons"), id='botao-add-produtos'),  # O botão que desencadeará o evento
                html.Button(html.Span("query_stats", className="material-icons"), id='botao-previsao'),  # O botão que desencadeará o evento
                html.Button(html.Span("settings", className="material-icons"), id='botao-config'),  # O botão que desencadeará o evento
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
        html.Div(id='page-content')
    ])

def main(): 

    app.layout = default_layout
    
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <title>Dash App with Google Icons</title>
            <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
            rel="stylesheet">
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
        
    app.run(debug=True, use_reloader=False)

#------------------------------------------------------ Páginas ----------------------------------------------------------------#
    
# ------------------------------------------------------ Dialog ----------------------------------------------------------------#
# Callback para abrir/fechar o modal
@app.callback(
    Output("modal", "is_open"),
    [Input("botao-add-produtos", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n1, is_open):
    return not is_open
    
# ------------------------------------------------------ Gráfico de barras ----------------------------------------------------------------#

if __name__ == "__main__":
    main()