from queue import Queue
from threading import Thread, Event
import random
import numpy as np
import time

hist = []

# Evento de controle
stop_event = Event()

def comprarProduto(queue, lambT, lambQ):
    data = []
    while not stop_event.is_set():
        tempo = geracaoTempo(lambT)
        quant = geracaoQuant(lambQ)
        data = {"quant": quant, "tempo": tempo}
        queue.put(data)

def geracaoTempo(lamb):
    return random.expovariate(lamb)
    
def geracaoQuant(lamb):
    quant = random.expovariate(lamb)
    quant = round(quant) + 1
    if quant < 1: quant = 1
    return quant

def simular_compra(queue, quantidade_produtos):
    # Enquanto houverem produtos permite a compra
    while quantidade_produtos > 0:
        dados = queue.get()
        quant = dados["quant"]
        if quant < quantidade_produtos:
            quantidade_produtos -= dados["quant"]
        else:
            quant = quantidade_produtos
            quantidade_produtos = 0
        hist.append(dados)
    stop_event.set()
    print(hist)

def main():
    # Parâmetros das variáveis aleatórias geradas
    lambT = 1
    lambQ = 1
    
    # Quantidade inicial de produtos
    quantidade_produtos = 1000
    
    # Fila
    queue = Queue()
    
    # Threads
    produto = Thread(target=comprarProduto, args=(queue, lambT, lambQ))
    comprar = Thread(target=simular_compra, args=(queue, quantidade_produtos))
    
    # Inicia
    produto.start()
    comprar.start()
    
    # Parar 
    comprar.join()
    produto.join()

if __name__ == "__main__":
    main()