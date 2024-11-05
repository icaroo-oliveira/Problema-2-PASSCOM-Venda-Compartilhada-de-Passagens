from flask import Flask, request, jsonify
import threading
import random
import time
from utils_server_a import *
from connection import *

app = Flask(__name__)

# Lock para a região crítica (acesso a arquivos e afins)
file_lock = threading.Lock()

HOST = '0.0.0.0'
PORTA = 65433

# Função que verifica se algum servidor alheio deu erro na realização de algum rollback, ou seja, tem rollback pendente
# Essa verificação é feita a cada nova requisição recebida pelo servidor
# Parâmetros ->     Sem parâmetros
# Retorno ->        Sem retorno
def tentar_rollback_novamente():
    with file_lock:
        rollback_data = carregar_rollbacks_failures()

        server_B = rollback_data["B"]
        server_C = rollback_data["C"]

        # Se nenhum servidor tem rollback pendente, encerra a função
        if not server_B and not server_C:
            return

        # Se servidor B tem rollback a realizar
        if server_B:
            resposta_rollback = requests_delete(SERVER_URL_B, "/rollback", server_B, "resultado", "B", 10)

            # Significa que rollback foi realizado, logo posso apagar do arquivo
            if resposta_rollback is not None:
                rollback_data["B"] = []
                salvar_rollbacks_failures(rollback_data)

        # Se servidor C tem rollback a realizar    
        if server_C:
            resposta_rollback = requests_delete(SERVER_URL_C, "/rollback", server_C, "resultado", "C", 10)

            # Significa que rollback foi realizado, logo posso apagar do arquivo
            if resposta_rollback is not None:
                rollback_data["C"] = []
                salvar_rollbacks_failures(rollback_data)

# Retorna caminhos encontrados de origem a destino (cliente pediu)
@app.route('/caminhos_cliente', methods=['GET'])
def handle_caminhos_cliente():
    tentar_rollback_novamente()

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
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "caminhos_encontrados", NOMES_SERVIDORES[i], resultados, "/caminhos_servidor", 10))
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
    tentar_rollback_novamente()

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
    tentar_rollback_novamente()

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
        thread = threading.Thread(target=solicitar_caminhos_ou_passagens, args=(servidor, mensagem, "passagens_encontradas", NOMES_SERVIDORES[i], resultados, "/passagens_servidor", 10))
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
    tentar_rollback_novamente()

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
    tentar_rollback_novamente()
        
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
                registra_trechos_escolhidos(G, trechos_server_a, cpf)
            
            # Se servidor A não tem mais o trecho, retorna ao cliente que deu merda
            else:
                return jsonify({"resultado": "Caminho indisponível"}), 300
    
    # Se não tem trechos a enviar nem pro server B e nem pro C, retorna compra realizada (só comprou no A)
    if not trechos_server_b and not trechos_server_c:
        return jsonify({"resultado": "Compra realizada com sucesso"}), 200

    # Se server A não tem caminho; server A tem caminho, está tudo disponível e server B e/ou C tem caminho; verifica com
    # os outros servidores

    mensagem = {
        "caminho": caminho,
        "cpf": cpf
    }
     
    # Dicionário para armazenar os resultados das requisições (compra feita ou não pelo outros servidores)
    respostas = {}

    # Cria threads para solicitar caminhos dos servidores B e C
    threads = []
    # time.sleep(10) para testes
    if trechos_server_b:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_B, mensagem, "resultado", "B", respostas, "/comprar_servidor", 10))
        threads.append(thread)
        thread.start()

    # print("indo para compra de C") para testes

    # time.sleep(20) #para testes
    if trechos_server_c:
        thread = threading.Thread(target=solicitar_comprar, args=(SERVER_URL_C, mensagem, "resultado", "C", respostas, "/comprar_servidor", 10))
        threads.append(thread)
        thread.start()
    
    # Aguarda todas as threads terminarem (se criou alguma)
    for thread in threads:
        thread.join()
    print("c nao tinha mais")
    time.sleep(10)
    # Retorna as respostas dos servidores (se tinha trechos A ENVIAR) ou retorna -1 (não tinha trechos A ENVIAR)
    # ps: só vai ser -1 se nem criou threads pra enviar ao servidor (nem tinha oq enviar)
    resposta_b, status_b = respostas.get("B", (-1, -1))
    resposta_c, status_c = respostas.get("C", (-1, -1))

    # Caso 1: Somente um dos 2 servidores tinha trechos a serem verificados e comprados

    # Se somente servidor C tinha trechos pra verificar e comprar
    if status_b == -1 and status_c != -1:
        # Se servidor C conseguiu comprar de boa
        if status_c == 200:
            print(resposta_c)
            return jsonify({"resultado": "Compra realizada com sucesso"}), 200
        # Se servidor C não tinha mais os trechos ou não respondeu
        else:
            # Se não tinha mais os trechos
            if status_c == 300:
                print(resposta_c)
            # Se server A registou a compra, desfaz
            if trechos_server_a:
                with file_lock:
                    desregistra_trechos_escolhidos(trechos_server_a, cpf)
            
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Se somente servidor B tinha trechos pra verificar e comprar
    if status_c == -1 and status_b != -1:
        # Se servidor B conseguiu comprar de boa
        if status_b == 200:
            print(resposta_b)
            return jsonify({"resultado": "Compra realizada com sucesso"}), 200
        # Se servidor B não tinha mais os trechos ou não respondeu
        else:
            # Se não tinha mais os trechos
            if status_b == 300:
                print(resposta_b)
            # Se server A registou a compra, desfaz
            if trechos_server_a:
                with file_lock:
                    desregistra_trechos_escolhidos(trechos_server_a, cpf)
            
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Caso 2: Ambos os servidores não tinham mais os trechos ou não respoderam
    if (status_b == 300 or status_b is None) and (status_c == 300 or status_c is None):
        if status_b == 300:
            print(resposta_b)
        
        if status_c == 300:
            print(resposta_c)

        # Se servidor A fez a compra, desfaz
        if trechos_server_a:
            with file_lock:
                desregistra_trechos_escolhidos(trechos_server_a, cpf)
            
            # Informa ao cliente que compra deu erro
            return jsonify({"resultado": "Caminho indisponível"}), 300

    # Caso 3: Ambos os servidores tiveram sucesso
    if status_b == 200 and status_c == 200:
        print(resposta_b)
        print(resposta_c)
        return jsonify({"resultado": "Compra realizada com sucesso"}), 200

    # Caso 4: Um servidor falha e o outro tem sucesso (realiza rollback no que teve sucesso)
    # ps: Caso o servidor A tenha realizado compra, também desfaz

    rollback = [mensagem]
        
    # Servidor C teve sucesso e servidor B não
    if (status_b == 300 or status_b is None) and status_c == 200:
        if status_b == 300:
            print(resposta_b)
        
        resposta_rollback = requests_delete(SERVER_URL_C, "/rollback", rollback, "resultado", "C", 10)

        if resposta_rollback is None:
            registrar_rollback(mensagem, "C")

    # Servidor B teve sucesso e servidor C não
    elif (status_c == 300 or status_c is None) and status_b == 200:
        if status_c == 300:
            print(resposta_c)
        
        resposta_rollback = requests_delete(SERVER_URL_B, "/rollback", rollback, "resultado", "B", 10)

        if resposta_rollback is None:
            registrar_rollback(mensagem, "B")

    print(resposta_rollback)

    if trechos_server_a:
        with file_lock:
            desregistra_trechos_escolhidos(trechos_server_a, cpf)
    return jsonify({"resultado": "Caminho indisponível"}), 300

# Verifica e registra compra de trechos (outro servidor pediu)
@app.route('/comprar_servidor', methods=['POST'])
def handle_comprar_servidor():
    tentar_rollback_novamente()

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
            comprar = verifica_trechos_escolhidos(G, trechos_server_a)

            # Quando trecho tiver disponível, sai do loop
            if comprar:
                # REGIÃO CRITICA
                registra_trechos_escolhidos(G, trechos_server_a, cpf)
                break

    # Se não tava mais disponível algum trecho
    if not comprar:
        return jsonify({"resultado": "Caminho indisponível no servidor A"}), 300
    
    return jsonify({"resultado": "Compra realizada com sucesso no servidor A"}), 200

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
            desregistra_trechos_escolhidos(trechos_server_a, cpf)

    return jsonify({"resultado": "Rollback realizado com sucesso no servidor A"})

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
        # time.sleep(10) para testes
