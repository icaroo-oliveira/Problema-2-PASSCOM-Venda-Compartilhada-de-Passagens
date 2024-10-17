from flask import Flask, request, jsonify
import threading

from utils_server_a import *
from connection import *

app = Flask(__name__)
 
file_lock = threading.Lock()

HOST = '0.0.0.0'
PORTA = 65433

SERVER_URL_B = "http://127.0.0.1:65434"
SERVER_URL_C = "http://127.0.0.1:65435"

# Retorna caminhos encontrados de origem a destino (cliente pediu)
@app.route('/caminhos_cliente', methods=['GET'])
def handle_caminhos_cliente():
    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']
    
    # Carrega grafo e encontra caminho do servidor A
    # REGIÃO CRITICA
    with file_lock:
        caminhos_a = encontrar_caminhos(origem, destino)

    mensagem = {
        "origem": origem,
        "destino": destino
    }

    # Dicionário para armazenar os resultados das requisições (caminhos encontrados ou não pelo outros servidores)
    resultados = {}

    # Cria threads para solicitar caminhos dos servidores B e C
    threads = []
    for i, servidor in enumerate([SERVER_URL_B, SERVER_URL_C], 1):
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "caminhos_encontrados", nomes_servidores[i], resultados, "/caminhos_servidor"))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()

    # Pega resposta das threads
    caminhos_b = resultados["B"]
    caminhos_c = resultados["C"]

    # Verifica qual servidor retornou pelo menos um caminho
    caminhos_servidores = servidor_encontrou_caminho(caminhos_a, caminhos_b, caminhos_c)

    # Pode ser que todos servidores não encontraram caminhos, cliente verifica!!!
    return jsonify({"caminhos_encontrados": caminhos_servidores})

# Retorna caminhos encontrados de origem a destino (outro servidor pediu)
@app.route('/caminhos_servidor', methods=['GET'])
def handle_caminhos_servidor():
    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']
    
    # Carrega grafo e encontra caminho do servidor A
    # REGIÃO CRITICA
    with file_lock:
        caminhos_a = encontrar_caminhos(origem, destino)

    return jsonify({"caminhos_encontrados": caminhos_a})

# Pra verificar compras de um cliente (cliente pediu)
@app.route('/passagens_cliente', methods=['GET'])
def handle_passagens_compradas_cliente():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega cpf do cliente
    cpf = data['cpf']

    # Verifica se tem passagens compradas por CPF no servidor A
    # REGIÃO CRITICA
    with file_lock:
        passagens_a = verifica_compras_cpf(cpf)

    mensagem = {
        "cpf": cpf
    }

    # Dicionário para armazenar os resultados das requisições (passagens encontradas ou não pelo outros servidores)
    resultados = {}

    # Cria threads para solicitar passagens dos servidores B e C
    threads = []
    for i, servidor in enumerate([SERVER_URL_B, SERVER_URL_C], 1):
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "passagens_encontradas", nomes_servidores[i], resultados, "/passagens_servidor"))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()

    # Pega resposta das threads
    passagens_b = resultados["B"]
    passagens_c = resultados["C"]

    # Verifica qual servidor retornou pelo menos uma passagem e adiona numa lista pra enviar ao cliente
    passagens_servidores = servidor_encontrou_passagem(passagens_a, passagens_b, passagens_c)

    return jsonify({"passagens_encontradas": passagens_servidores})

# Pra verificar compras de um cliente (outro servidor pediu)
@app.route('/passagens_servidor', methods=['GET'])
def handle_passagens_compradas_servidor():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega cpf do cliente
    cpf = data['cpf']

    # Verifica se tem passagens compradas por CPF no servidor A
    # REGIÃO CRITICA
    with file_lock:
        passagens_a = verifica_compras_cpf(cpf)

    return jsonify({"passagens_encontradas": passagens_a})

# Verifica e registra compra de trechos (cliente pediu)
@app.route('/comprar_cliente', methods=['POST'])
def handle_comprar_cliente():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega caminho e cpf escolhido pelo cliente
    caminho = data['caminho']
    cpf = data['cpf']

    # Separa cada trecho do caminho ao seu devido servidor
    trechos_server_a, trechos_server_b, trechos_server_c = desempacota_caminho_cliente(caminho)

    # Servidor A tem pelo menos um trecho
    if trechos_server_a:
        with file_lock:
            G = carregar_grafo()
            comprar = verifica_trechos_escolhidos(G, trechos_server_a)

            # Se servidor A ainda tem os trechos, registra a compra
            if comprar:
                # PS: aqui vai ter que retirar a compra depois, caso server B ou C de merda
                registra_trechos_escolhidos(G, trechos_server_a, cpf)
            
            # Se servidor A não tem mais o trecho, retorna ao cliente que deu merda
            else:
                return jsonify({"resultado": "Caminho indisponível"}), 400

    # Se server A não tem caminho ou se server A tem caminho e está tudo disponível, verifica com
    # os outros servidores

    mensagem = {
        "caminho": caminho,
        "cpf": cpf
    }
     
    # Dicionário para armazenar os resultados das requisições (compra feita ou não pelo outros servidores)
    respostas = {}

    # Cria threads para solicitar caminhos dos servidores B e C
    threads = []

    if trechos_server_b:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_B, mensagem, "resultado", "B", respostas, "/comprar_servidor"))
        threads.append(thread)
        thread.start()

    if trechos_server_c:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_C, mensagem, "resultado", "C", respostas, "/comprar_servidor"))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem (se criou alguma)
    for thread in threads:
        thread.join()

    # Pega resposta das threads
    if "B" in respostas:
        resposta_b, status_b = respostas["B"]
    
    if "C" in respostas:
        resposta_c, status_c = respostas["C"]
        

    # Aqui tem que verificar resposta dos servidores para ver se conseguiu comprar ou nao


    return jsonify({"resultado": "Compra realizada com sucesso"}), 200
        
# Verifica e registra compra de trechos (outro servidor pediu)
@app.route('/comprar_servidor', methods=['POST'])
def handle_comprar_servidor():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega caminho e cpf escolhido pelo cliente
    caminho = data['caminho']
    cpf = data['cpf']

    # Separa cada trecho do caminho ao seu devido servidor
    trechos_server_a, trechos_server_b, trechos_server_c = desempacota_caminho_cliente(caminho)

    # Verifica se seus trechos ainda tao disponíveis
    # REGIÃO CRITICA
    with file_lock:
        G = carregar_grafo()
        comprar = verifica_trechos_escolhidos(G, trechos_server_a)

        if comprar:
            # REGIÃO CRITICA
            registra_trechos_escolhidos(G, trechos_server_a, cpf)

            return jsonify({"resultado": "Compra realizada com sucesso"}), 200

        # Por enquanto só retorna que a compra deu merda
        else:
            return jsonify({"resultado": "Caminho indisponível"}), 400

if __name__ == "__main__":
    # O Flask usa `run` para iniciar o servidor HTTP
    cria_arquivo_grafo()

    try:
        # host -> servidor acessível por outros dispositivos na mesma rede
        # port -> do servidor em questão
        # threaded -> multiplas requisições processadas ao "mesmo tempo"
        app.run(host=HOST, port=PORTA, threaded=True)

    # Se app.run der merda, exibe a merda e encerra programa
    except (OSError, Exception) as e:
        print(f"Erro: {e}")
