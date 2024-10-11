from flask import Flask, request, jsonify

import requests

from utils_server_a import *

app = Flask(__name__)

server_url_b = "http://127.0.0.1:65434"
server_url_c = "http://127.0.0.1:65435"

# Retorna caminhos encontrados de origem a destino
@app.route('/caminhos', methods=['GET'])
def handle_caminhos():
    # Retorna caminhos encontrados por servidor A, B e C
    caminhos_servidores = []

    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']
    
    # Carrega grafo e encontra caminho do servidor A
    G = carregar_grafo()
    caminhos_A = encontrar_caminhos(G, origem, destino)

    mensagem = {
        "origem":origem,
        "destino":destino
    }

    # Recebe caminhos do server B e C
    caminhos_B, caminhos_C = []



    # Aqui adiciona thread para pedir caminho do server B e C ao mesmo tempo



    try:
        #usando get, para encontrar os caminhos de {origem} a {destino} do server B
        response_B = requests.get(server_url_b+"/caminhos", json=mensagem, timeout=10)
        response_B.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Caminhos encontrados pelo server B
        caminhos_B = response_B.json()["caminhos_encontrados"]
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro: {e}") 

    try:
        #usando get, para encontrar os caminhos de {origem} a {destino} do server C
        response_C = requests.get(server_url_c+"/caminhos", json=mensagem, timeout=10)
        response_C.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
        
        # Caminhos encontrados pelo server C
        caminhos_C = response_C.json()["caminhos_encontrados"]
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro: {e}") 

    # Verifica qual servidor retornou pelo menos um caminho e adiona numa lista pra enviar ao cliente
    caminhos_servidores = servidor_encontrou_caminho(caminhos_A, caminhos_B, caminhos_C)

    # Pode ser que nenhum servidor retornou nenhum caminho, cliente verifica!!!
    return jsonify({"caminhos_encontrados": caminhos_servidores})
    
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
    cria_arquivo_grafo()

    # Do jeito que tá, somente uma requisição é processada por vez
    # Se outra requisição chegar enquanto uma ta sendo processada
    # O proprio flask ja adicionada numa fila e gerencia essa fila
    try:
        # host -> servidor acessível por outros dispositivos na mesma rede
        # port -> do servidor em questão
        app.run(host='0.0.0.0', port=65433)

    # Se app.run der merda, exibe a merda e encerra programa
    except (OSError, Exception) as e:
        print(f"Erro: {e}")

    
