from flask import Flask, request, jsonify
import json
import threading
import queue
from utils_server import *
import requests
import time
B_Receive_buffer = None


app = Flask(__name__)

# Condição e Lock para controle de threads e acesso à região crítica
#condition = threading.Condition()
lock = threading.Lock()

# Fila de threads (FIFO)
#waiting_queue = queue.Queue()

# se for usar trhead, coloca a logica das FIFOS para thread e codition aq dentro
#funcao = funcao que quero executar...
def process_threaded_task(funcao, *args):

    #     current_thread = threading.current_thread()
    #     adicionar_thread_fila(condition, current_thread, waiting_queue)
    #     with lock:
    #     result = task_function(*args)
    #     remover_thread_fila(condition, current_thread, waiting_queue)

  
    result = funcao(*args)
    
    return result


#para acesso aos caminhos de {origem} até {destino}
@app.route('/caminhos', methods=['GET'])
def handle_caminhos():
    #transformando em dic 
    data = request.json
    #fazendo mesmo que antes
    origem = data['origem']
    destino = data['destino']
    origem = cidades[int(origem) - 1]
    destino = cidades[int(destino) - 1]
    print(origem,destino)
    # Processo de encontrar caminhos com threading
    def tarefa_caminhos(origem, destino):
    
        G = carregar_grafo_B()
        
        caminhos = encontrar_caminhos(G, origem, destino)
        print(caminhos)
        return caminhos

    caminhos = process_threaded_task(tarefa_caminhos, origem, destino)
    return jsonify({"caminhos_encontrados": caminhos})
    
    




#para regiistrar a compra de uma pasagem
@app.route('/caminhos', methods=['POST'])
def handle_comprar():
    data = request.json
    caminho = data['caminho']
    cpf = data['cpf']
    

    #isso é novo, é retornando uma lista, mas é preciso que com essa lista se construa um caminho
    #['cuiabá', 'sao paulo', 'minas', 'salvador'] vira --> [('cuiabá', 'sao paulo'), ('sao paulo', 'minas'), ('minas', 'salvador')]
    pares_consecutivos = []
    for i in range(len(caminho) - 1):
        par = (caminho[i], caminho[i + 1]) 
        pares_consecutivos.append(par)

    #mesma coisa de antes, so não procura mais por outros trechos...
    def tarefa_comprar(pares_consecutivos, cpf):#tava caminho antes
        G = carregar_grafo()
        with lock:
            if verifica_trechos_escolhidos(G, pares_consecutivos):
                print("alalalalalal")
                registra_trechos_escolhidos(G, pares_consecutivos, cpf)
                return "Compra realizada com sucesso"
            else:
                return "Caminho indisponível"

    resultado = process_threaded_task(tarefa_comprar, pares_consecutivos, cpf)

    return jsonify({"resultado": resultado})


#método pra visualizar as passagens por cpf...(arrumar)
@app.route('/passagens', methods=['GET'])
def handle_passagens_compradas():
    data = request.json
    cpf = data['cpf']
    print(cpf)
    # Processo de verificar passagens com threading
    def tarefa_passagens(cpf):
        compras = verifica_compras_cpf(cpf)
        return compras

    passagens = process_threaded_task(tarefa_passagens, cpf)
    return jsonify({"passagens_encontradas": passagens})








if __name__ == "__main__":
    # O Flask usa `run` para iniciar o servidor HTTP
    cria_arquivo_grafo_B()
    app.run(host='0.0.0.0', port=65434)
    


