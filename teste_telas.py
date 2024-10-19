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

lock = Lock()

df = pd.DataFrame(columns=['quant', 'data', 'id_produto'])
df = select()

produtos = pd.DataFrame(columns=['id_produto', 'nome_produto'])
produtos = obterProdutos()

df_bar = pd.DataFrame(columns=['id_produto', 'quant_total'])
df_bar = obterVendas()

selected_itemsGeral = []

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

def geracaoTempo():
    return random.expovariate(1)
    
def geracaoQuant():
    quant = random.randint(1, 5)
    return quant

def generate_random_numbers(queue, quant_estoque, id_produto):
    global df
    quant_total = df_bar.loc[df_bar['id_produto'] == id_produto, 'quant_total']
    while quant_estoque > 0:
        # with lock:
            data = queue.get()
            quant = data['quant']
            date = data['data']
            quant_estoque = quant_estoque - quant
            quant_total = quant_total + quant
            if quant_estoque < 0:
                quant = quant + quant_estoque
                quant_estoque = 0
            new_row = {'quant': quant_estoque, 'data': date, 'id_produto': id_produto}
            df.loc[len(df)] = new_row
            df_bar.loc[df_bar['id_produto'] == id_produto, 'quant_total'] = quant_total
            saveDB(quant, date, quant_estoque, id_produto)
            if quant_estoque == 0:
                quant_estoque = 200

app = Dash(suppress_callback_exceptions=True, external_stylesheets=["https://fonts.googleapis.com/icon?family=Material+Icons", 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css', dbc.themes.BOOTSTRAP])

default_layout = html.Div([
        dcc.Location(id='url', refresh=False),
        dcc.Location(id='url2', refresh=False),
        dcc.Store(id='dropdown-values'),
        html.Div([
                html.Button(html.Span("home", className="material-icons"), id='botao-home',),  # O botão que desencadeará o evento
                html.Button(html.Span("add", className="material-icons"), id='botao-add-produtos'),  # O botão que desencadeará o evento
                html.Button(html.Span("query_stats", className="material-icons"), id='botao-previsao'),  # O botão que desencadeará o evento
                html.Button(html.Span("settings", className="material-icons"), id='botao-config'),  # O botão que desencadeará o evento
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
        html.Div(id='page-content')
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
        
        thread[i] = Thread(target=generate_random_numbers, args=(queue[i], quant_estoque[i], produtos["id_produto"].loc[i] ))
        thread[i].start()

    app.layout = default_layout
    
    # app.index_string = '''
    # <!DOCTYPE html>
    # <html>
    #     <head>
    #         <meta charset="utf-8">
    #         <title>Dash App with Google Icons</title>
    #         <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    #         <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    #     </head>
    #     <body>
    #         {%app_entry%}
    #         <footer>
    #             {%config%}
    #             {%scripts%}
    #             {%renderer%}
    #         </footer>
    #     </body>
    # </html>
    # '''
        
    app.run(debug=True, use_reloader=False)
    
@callback(
    Output('url', 'pathname'),  # O output vai alte rar o pathname da URL
    [Input('botao-home', 'n_clicks'),
    #  Input('botao-add-produtos', 'n_clicks'),
     Input('botao-previsao', 'n_clicks'),
     Input('botao-config', 'n_clicks'),
     ],
    Input('url', 'pathname'),  # O input que captura o pathname atual
)
def redirecionar_page(n1, n3, n4, pathname):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    # Identifica qual botão foi clicado
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'botao-home' and n1:
        return '/home'
    # elif button_id == 'botao-add-produtos' and n2:
    #     return '/add_produto'
    elif button_id == 'botao-previsao' and n3:
        return '/previsao'
    elif button_id == 'botao-config' and n4:
        return '/config'

    return pathname

#------------------------------------------------------ Páginas ----------------------------------------------------------------#

@callback(Output('page-content', 'children'),
            Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/home' or pathname == '/':
        global selected_itemsGeral
        dropdown_options = get_options_from_db()
        layout = html.Div([html.H1(children='Monitoramento de estoque', style={'textAlign':'center'}),
                            # dcc.Store(id='data-store'),
                            dcc.Interval(id='interval-start', interval=1, n_intervals=0, max_intervals=1),  # Executa apenas uma vez no início
                            dbc.Modal(
                                [
                                    dcc.Interval(id='interval-dropdown', interval=1, n_intervals=0, max_intervals=1),  # Executa apenas uma vez no início
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
                                            html.Button('Adicionar', id='botao-criar', style={'width': '150px', 'height': '50px', 'font-size': '25px'}),  # O botão que desencadeará o evento
                                        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
                                    ),
                                ],
                                id="modal",
                                is_open=False,
                                size="lg",  # Definido para grande, pode ser "sm", "lg" ou "xl"
                                backdrop=True,  # Permite fechar ao clicar fora do modal
                                keyboard=True,  # Permite fechar ao pressionar "ESC"
                                centered=True,  # Centralizado na tela
                            ),
                            html.Div(id='graphs-container', style={'display': 'flex', 'flex-wrap': 'wrap'}),
                            dcc.Interval(
                                id='interval-component',
                                interval=500,
                                n_intervals=0,
                            ),
                            dcc.Graph(
                                id='bar-graph',
                            ),
                            html.P("Ranking", style={'textAlign':'center'}),
                            html.Div(id='dynamic-content', style={'textAlign':'center'})
                            ]),
        return layout
    # elif pathname == '/add_produto':
    #     global selected_itemsGeral
    #     dropdown_options = get_options_from_db()
    #     layout2 = html.Div([html.H1(children='Adicionar produtos', style={'textAlign':'center'}),
    #                         dcc.Interval(id='interval-dropdown', interval=1, n_intervals=0, max_intervals=1),  # Executa apenas uma vez no início
    #                         dcc.Dropdown(
    #                             id='dropdown-produto',
    #                             options=dropdown_options,
    #                             placeholder="Selecione uma opção",
    #                             value=selected_itemsGeral,
    #                             multi=True,
    #                             style={'width': '100%'}
    #                         ),
    #                         html.Div([
    #                             html.Button('Adicionar', id='botao-criar', style={'width': '150px', 'height': '50px', 'font-size': '25px'}),  # O botão que desencadeará o evento
    #                         ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'width': '100%', 'padding-top': '20px'}),
    #                         ]),
    #     return layout2
    elif pathname == '/previsao':
        layout2 = html.Div([html.H1(children='Previsão', style={'textAlign':'center'})]),
        return layout2
    elif pathname == '/config':
        layout2 = html.Div([html.H1(children='Config', style={'textAlign':'center'}),]),
        return layout2
    else:
        return html.Div('Página Inexistente')
    
# ------------------------------------------------------ Dialog ----------------------------------------------------------------#
# Callback para abrir/fechar o modal
@callback(
    Output("modal", "is_open"),
    [Input("botao-add-produtos", "n_clicks"), Input("botao-criar", "n_clicks")],
    [dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    # Lógica para verificar qual botão foi pressionado
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return is_open  # Se nenhum botão foi pressionado, manter o estado atual
    
    # Verifica qual botão foi pressionado
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "botao-add-produtos" and not is_open:
        return True  # Abrir o modal se não estiver aberto
    elif button_id == "botao-criar" and is_open:
        return False  # Fechar o modal se estiver aberto
    
    return is_open  # Retorna o estado atual se nenhuma condição foi satisfeita
    
# ------------------------------------------------------ Gráfico de barras ----------------------------------------------------------------#

@callback(
    Output('bar-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_bar_chart(n_intervals):
    # Filtro baseado nos itens selecionados (supondo que você faça uma consulta no BD ou tenha uma lógica para isso)
    # Atualize os dados com base nos itens selecionados.
    
    df_merged = pd.merge(df_bar, produtos, on='id_produto')
    df_merged['nome_produto']
    
    # Exemplo de gráfico de barras dinâmico
    fig = px.bar(df_merged,
        x='nome_produto',  # Eixo X (atualizado dinamicamente)
        y='quant_total',  # Eixo Y (atualizado dinamicamente)
        labels={"nome_produto": "Produto", "quant_total": "Quantidade"},
        color='nome_produto',
        title="Vendas de produtos",
    )
    
    fig.update_layout(showlegend=False)
    
    return fig

# --------------------------------------------------------------------------------------------------------------------------------------------#
def criar_threads_produto():
    global produtos
    global df
    
    produtos = obterProdutos()
    df = select()
    
    quant_estoque = obterEstoqueAtual()
    # Fila
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
    # Input('botao-criar', 'n_clicks'), 
    Input("modal", "is_open"),
    State('dropdown-produto', 'value'),
)
def adicionar_grafico(n_clicks, selected_items):
    global selected_itemsGeral
    if selected_items is None or len(selected_items) == 0:
        return []
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
    # [Input('data-store', 'data')]
    Input('dropdown-produto', 'value'),
    # [Input('botao-home', 'n_clicks'), Input('botao-criar', 'n_clicks')], # Dispara na primeira vez
    [State('dropdown-values', 'data')],
)
def update_layout(n, dropdown_values):
    graphs = []
    # produtos = obterProdutos()
    print(dropdown_values)
    produtos = dropdown_values
    if not(produtos): produtos = []

    for i in produtos:
        # Adiciona um título e um gráfico para cada produto
        graph_div = html.Div([
            dcc.Graph(id={'type': 'product-figures', 'index': i})
        ], style={'width': '48%', 'display': 'inline-block', 'margin': '1%'})  # Controla o tamanho de cada gráfico e espaço

        graphs.append(graph_div)

    return graphs

#------------------------------------------------------ Atualização Gráficos ----------------------------------------------------------------#
# Callback para atualizar cada gráfico com base nos produtos
@callback(
    # [Output(f'graph-{i}', 'figure') for i in range(len(produtos))],
    Output({"type": "product-figures", "index": ALL}, "figure"),
    [Input('interval-component', 'n_intervals')],
    [State('dropdown-values', 'data')]
)
def update_graphs(n, dropdown_values):
    
    global df
    dff = df
    
    graficos = []
    
    global produtos
    
    teste = produtos[produtos['id_produto'].isin(dropdown_values)]
    
    for indice, linha in teste.iterrows():
        id = linha.id_produto
        name = linha.nome_produto
        graficos.append(GraficoProduto(go.Figure(data=go.Scatter(x=dff['data'].loc[dff['id_produto'] == id], y=dff['quant'].loc[dff['id_produto'] == id], mode="lines")),id,name))
    
    for fig in graficos:
            fig.grafico.update_layout(uirevision='some-constant', showlegend=False, xaxis_autorange=True, yaxis_autorange=True, autosize=True, title=fig.name)
            # fig.grafico.update_layout(showlegend=False, xaxis_autorange=True, yaxis_autorange=True, autosize=True, title=fig.name)
    
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