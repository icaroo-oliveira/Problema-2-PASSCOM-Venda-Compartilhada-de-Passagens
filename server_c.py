from flask import Flask, request, jsonify
import threading
import random
import time

from utils_server_c import *
from connection import *

app = Flask(__name__)

# Lock para a região crítica (acesso a arquivos e afins)
file_lock = threading.Lock()

HOST = '0.0.0.0'
PORTA = 65435

# Função que verifica se algum servidor alheio deu erro na realização de algum rollback, ou seja, tem rollback pendente
# Essa verificação é feita a cada nova requisição recebida pelo servidor
# Parâmetros ->     Sem parâmetros
# Retorno ->        Sem retorno
def tentar_rollback_novamente():
    with file_lock:
        rollback_data = carregar_rollbacks_failures()

        server_A = rollback_data["A"]
        server_B = rollback_data["B"]

        # Se nenhum servidor tem rollback pendente, encerra a função
        if not server_A and not server_B:
            return

        # Se servidor A tem rollback a realizar
        if server_A:
            resposta_rollback = requests_delete(SERVER_URL_A, "/rollback", server_A, "resultado", "A", 7)

            # Significa que rollback foi realizado, logo posso apagar do arquivo
            if resposta_rollback is not None:
                print(resposta_rollback)
                rollback_data["A"] = []
                salvar_rollbacks_failures(rollback_data)

        # Se servidor B tem rollback a realizar    
        if server_B:
            resposta_rollback = requests_delete(SERVER_URL_B, "/rollback", server_B, "resultado", "B", 7)

            # Significa que rollback foi realizado, logo posso apagar do arquivo
            if resposta_rollback is not None:
                print(resposta_rollback)
                rollback_data["B"] = []
                salvar_rollbacks_failures(rollback_data)

# Retorna caminhos encontrados de origem a destino (cliente pediu)
@app.route('/caminhos_cliente', methods=['GET'])
def handle_caminhos_cliente():
    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']
    
    # Carrega grafo e encontra caminho do servidor C
    # REGIÃO CRITICA
    with file_lock:
        caminhos_c = encontrar_caminhos(origem, destino)

    mensagem = {
        "origem": origem,
        "destino": destino
    }

    # Dicionário para armazenar os resultados das requisições (caminhos encontrados ou não pelo outros servidores)
    resultados = {}

    # Cria threads para solicitar caminhos dos servidores A e B
    threads = []
    for i, servidor in enumerate([SERVER_URL_A, SERVER_URL_B]):
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "caminhos_encontrados", NOMES_SERVIDORES[i], resultados, "/caminhos_servidor", 10))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()

    # Pega resposta das threads
    caminhos_a = resultados["A"]
    caminhos_b = resultados["B"]

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
    
    # Carrega grafo e encontra caminho do servidor C
    # REGIÃO CRITICA
    with file_lock:
        caminhos_c = encontrar_caminhos(origem, destino)

    return jsonify({"caminhos_encontrados": caminhos_c})

# Pra verificar compras de um cliente (cliente pediu)
@app.route('/passagens_cliente', methods=['GET'])
def handle_passagens_compradas_cliente():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega cpf do cliente
    cpf = data['cpf']

    # Verifica se tem passagens compradas por CPF no servidor C
    # REGIÃO CRITICA
    with file_lock:
        passagens_c = verifica_compras_cpf(cpf)

    mensagem = {
        "cpf": cpf
    }

    # Dicionário para armazenar os resultados das requisições (passagens encontradas ou não pelo outros servidores)
    resultados = {}

    # Cria threads para solicitar passagens dos servidores A e B
    threads = []
    for i, servidor in enumerate([SERVER_URL_A, SERVER_URL_B]):
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "passagens_encontradas", NOMES_SERVIDORES[i], resultados, "/passagens_servidor", 10))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem
    for thread in threads:
        thread.join()

    # Pega resposta das threads
    passagens_a = resultados["A"]
    passagens_b = resultados["B"]

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

    # Verifica se tem passagens compradas por CPF no servidor C
    # REGIÃO CRITICA
    with file_lock:
        passagens_c = verifica_compras_cpf(cpf)

    return jsonify({"passagens_encontradas": passagens_c})

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

    # Servidor C tem pelo menos um trecho
    if trechos_server_c:
        with file_lock:
            G = carregar_grafo()
            comprar = verifica_trechos_escolhidos(G, trechos_server_c)

            # Se servidor C ainda tem os trechos, registra a compra
            if comprar:
                # PS: aqui vai ter que retirar a compra depois, caso server A ou B de merda
                registra_trechos_escolhidos(G, trechos_server_c, cpf)
            
            # Se servidor C não tem mais o trecho, retorna ao cliente que deu merda
            else:
                return jsonify({"resultado": "Caminho indisponível"}), 300

    # Se não tem trechos a enviar nem pro server B e nem pro A, retorna compra realizada (só comprou no C)
    if not trechos_server_b and not trechos_server_a:
        return jsonify({"resultado": "Compra realizada com sucesso"}), 200

    # Se server C não tem caminho; server C tem caminho, está tudo disponível e server B e/ou A tem caminho; verifica com
    # os outros servidores

    mensagem = {
        "caminho": caminho,
        "cpf": cpf
    }
     
    # Dicionário para armazenar os resultados das requisições (compra feita ou não pelo outros servidores)
    respostas = {}

    # Cria threads para solicitar caminhos dos servidores B e A
    threads = []

    if trechos_server_b:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_B, mensagem, "resultado", "B", respostas, "/comprar_servidor", 10))
        threads.append(thread)
        thread.start()

    if trechos_server_a:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_A, mensagem, "resultado", "A", respostas, "/comprar_servidor", 10))
        threads.append(thread)
        thread.start()

    # Aguarda todas as threads terminarem (se criou alguma)
    for thread in threads:
        thread.join()

    # Retorna as respostas dos servidores (se tinha trechos A ENVIAR) ou retorna -1 (não tinha trechos A ENVIAR)
    # ps: só vai ser -1 se nem criou threads pra enviar ao servidor (nem tinha oq enviar)
    resposta_b, status_b = respostas.get("B", (-1, -1))
    resposta_a, status_a = respostas.get("A", (-1, -1))

    # Caso 1: Somente um dos 2 servidores tinha trechos a serem verificados e comprados

    # Se somente servidor A tinha trechos pra verificar e comprar
    if status_b == -1 and status_a != -1:
        # Se servidor A conseguiu comprar de boa
        if status_a == 200:
            print(resposta_a)
            return jsonify({"resultado": "Compra realizada com sucesso"}), 200
        # Se servidor A não tinha mais os trechos ou não respondeu
        else:
            # Se não tinha mais os trechos
            if status_a == 300:
                print(resposta_a)
            # Se server C registou a compra, desfaz
            if trechos_server_c:
                with file_lock:
                    desregistra_trechos_escolhidos(trechos_server_c, cpf)
            
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Se somente servidor B tinha trechos pra verificar e comprar
    if status_a == -1 and status_b != -1:
        # Se servidor B conseguiu comprar de boa
        if status_b == 200:
            print(resposta_b)
            return jsonify({"resultado": "Compra realizada com sucesso"}), 200
        # Se servidor B não tinha mais os trechos ou não respondeu
        else:
            # Se não tinha mais os trechos
            if status_b == 300:
                print(resposta_b)
            # Se server C registou a compra, desfaz
            if trechos_server_c:
                with file_lock:
                    desregistra_trechos_escolhidos(trechos_server_c, cpf)
            
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Caso 2: Ambos os servidores tiveram sucesso
    if status_b == 200 and status_a == 200:
        print(resposta_b)
        print(resposta_a)
        return jsonify({"resultado": "Compra realizada com sucesso"}), 200

    # Caso 3: Ambos os servidores não tinham mais os trechos ou não respoderam
    if (status_b == 300 or status_b is None) and (status_a == 300 or status_a is None):
        if status_b == 300:
            print(resposta_b)
        
        if status_a == 300:
            print(resposta_a)

        # Se servidor C fez a compra, desfaz
        if trechos_server_c:
            with file_lock:
                desregistra_trechos_escolhidos(trechos_server_c, cpf)
            
            # Informa ao cliente que compra deu erro
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Caso 4: Um servidor falha e o outro tem sucesso (realiza rollback no que teve sucesso)
    # ps: Caso o servidor C tenha realizado compra, também desfaz

    rollback = [mensagem]

    # Servidor A teve sucesso e servidor B não
    if (status_b == 300 or status_b is None) and status_a == 200:
        if status_b == 300:
            print(resposta_b)
            
        resposta_rollback = requests_delete(SERVER_URL_A, "/rollback", rollback, "resultado", "A", 10)

        # Se servidor A não realizou rollback (off ou sem rede), registro par tentar de novo em outro momento
        if resposta_rollback is None:
            registrar_rollback(mensagem, "A")

    # Servidor B teve sucesso e servidor A não
    elif (status_a == 300 or status_a is None) and status_b == 200:
        if status_a == 300:
            print(resposta_a)
        
        resposta_rollback = requests_delete(SERVER_URL_B, "/rollback", rollback, "resultado", "B", 10)

        # Se servidor B não realizou rollback (off ou sem rede), registro par tentar de novo em outro momento
        if resposta_rollback is None:
            registrar_rollback(mensagem, "B")

    print(resposta_rollback)

    if trechos_server_c:
        with file_lock:
            desregistra_trechos_escolhidos(trechos_server_c, cpf)

    return jsonify({"resultado": "Caminho indisponível"}), 300
        
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

    # Quantidade de vezes que a thread vai verificar se o trecho ta disponível
    qtd_for = random.randint(1, 5)

    for i in range(qtd_for):
        # Tempo random (100ms a 300ms) para thread verificar se o trecho ta disponível novamente
        time.sleep(times[random.randint(0, 4)])

        # Verifica se seus trechos ainda tao disponíveis
        # REGIÃO CRITICA
        with file_lock:
            G = carregar_grafo()
            comprar = verifica_trechos_escolhidos(G, trechos_server_c)

            # Quando trecho tiver disponível, sai do loop
            if comprar:
                # REGIÃO CRITICA
                registra_trechos_escolhidos(G, trechos_server_c, cpf)
                break

    # Se não tava mais disponível algum trecho
    if not comprar:
        return jsonify({"resultado": "Caminho indisponível no servidor C"}), 300
    
    return jsonify({"resultado": "Compra realizada com sucesso no servidor C"}), 200

# Ordem de rollback (desfaz compra caso outro servidor não consiga realizar sua compra)
@app.route('/rollback', methods=['DELETE'])
def handle_rollback():
    # Transforma mensagem do servidor em dicionário
    data = request.json
    
    # REGIÃO CRITICA
    with file_lock:
        for rollback in data:
            # Pega caminho e cpf escolhido a desfazer a compra
            caminho = rollback['caminho']
            cpf = rollback['cpf']

            # Separa cada trecho do caminho ao seu devido servidor
            trechos_server_a, trechos_server_b, trechos_server_c = desempacota_caminho_cliente(caminho)

            # Desfaz a compra
            # Adiciona assento aos trechos, remove cpf dos trechos e remove compra associada ao cpf
            desregistra_trechos_escolhidos(trechos_server_c, cpf)

    return jsonify({"resultado": "Rollback realizado com sucesso no servidor C"})

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
