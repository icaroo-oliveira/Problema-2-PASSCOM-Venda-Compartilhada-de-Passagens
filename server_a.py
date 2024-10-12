from flask import Flask, request, jsonify

from utils_server_a import *
from connection import *

app = Flask(__name__)

SERVER_URL_B = "http://127.0.0.1:65434"
SERVER_URL_C = "http://127.0.0.1:65435"

# Retorna caminhos encontrados de origem a destino
@app.route('/caminhos', methods=['GET'])
def handle_caminhos():
    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']

    # Lista para armazenar caminhos encontrados por servidor A, B e C
    caminhos_servidores = []
    
    # Carrega grafo e encontra caminho do servidor A
    G = carregar_grafo()
    caminhos_a = encontrar_caminhos(G, origem, destino)

    # Pra receber caminhos do server B e C
    caminhos_b, caminhos_c = []

    mensagem = {
        "origem": origem,
        "destino": destino
    }



    # Aqui adiciona thread para pedir caminho do server B e C ao mesmo tempo



    # Caminhos encontrados pelo server B
    caminhos_b = requests_get(SERVER_URL_B, "/caminhos", mensagem, "caminhos_encontrados", "B")

    # Caminhos encontrados pelo server C
    caminhos_c = requests_get(SERVER_URL_C, "/caminhos", mensagem, "caminhos_encontrados", "C")



    # Verifica qual servidor retornou pelo menos um caminho e adiona numa lista pra enviar ao cliente
    caminhos_servidores = servidor_encontrou_caminho(caminhos_a, caminhos_b, caminhos_c)

    # Pode ser que todos servidores não encontraram caminhos, cliente verifica!!!
    return jsonify({"caminhos_encontrados": caminhos_servidores})
    
# Verifica e registra compra de trechos
@app.route('/comprar', methods=['POST'])
def handle_comprar():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega caminho e cpf escolhido pelo cliente
    caminho = data['caminho']
    cpf = data['cpf']
    
    # Aqui vai usar para encontrar novamente caminhos novos caso algum server não tenha mais os trechos
    origem = caminho[1][0]
    destino = caminho[1][len(caminho[1]) - 1]

    # Separa cada trecho do caminho ao seu devido servidor
    trechos_server_a, trechos_server_b, trechos_server_c = desempacota_caminho_cliente(caminho)

    G = carregar_grafo()
    
    # Vê se trechos do server A ainda tão disponíveis
    comprar = verifica_trechos_escolhidos(G, trechos_server_a)


    # Aqui que a merda acontece, não posso gravar a compras dos trechos no arquivo do server A, porque se
    # o server B ou C não tiver mais os seus trechos disponíveis, não posso gravar em nenhum server.
    # Teria que verificar nos 3 server ao mesmo tempo e gravar neles ao mesmo tempo

    # Por enquanto ta o cenário perfeito, server A consegue se comunicar com B e C, e eles
    # conseguem comprar os trechos numa boa


    # Se servidor A tem os trechos ainda, envia os trechos do B e C para eles registrarem a compra tbm
    if comprar:
        mensagem = {
            "caminho": caminho,
            "cpf": cpf
        }


        # Aqui adiciona thread para ENVIAR trechos do server B e C ao mesmo tempo


        # Se tiver algum trecho a enviar ao server B
        if trechos_server_b:

            # Resposta da compra do server B
            resposta_b = requests_post(SERVER_URL_B, "/comprar", mensagem, "resultado", "B")
            print(f"{resposta_b}")

        # Se tiver algum trecho a enviar ao server C
        if trechos_server_c:

            # Resposta da compra do server B
            resposta_c = requests_post(SERVER_URL_C, "/comprar", mensagem, "resultado", "C")
            print(f"{resposta_c}")

        # Como B e C já registrou a compra, server A registra tbm
        registra_trechos_escolhidos(G, trechos_server_a, cpf)

        return jsonify({"resultado": "Compra realizada com sucesso"})

    # Se trechos do server A não tiverem mais disponíveis, nem precisa enviar os trechos do server B e C para eles
    # Aqui tem que implementar para caso A não tenha mais, ele peça pro B e C para enviar novamente seus caminhos encontrados
    # de origem a destino e devolver pro cliente novamente 

    # Por enquanto só retorna que a compra deu merda
    else:
        return jsonify({"resultado": "Caminho indisponível"})

# Pra verificar compras de um cliente
@app.route('/passagens', methods=['GET'])
def handle_passagens_compradas():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega cpf do cliente
    cpf = data['cpf']

    # Lista para armazenar passagens encontrados por servidor A, B e C
    passagens_servidores = []

    # Verifica se tem passagens compradas por CPF no servidor A
    passagens_a = verifica_compras_cpf(cpf)

    # Pra receber passagens do server B e C
    passagens_b, passagens_c = []

    mensagem = {
        "cpf":cpf
    }


    # Aqui adiciona thread para pedir passagens do server B e C ao mesmo tempo


    # Passagens encontrados pelo server B
    passagens_b = requests_get(SERVER_URL_B, "/passagens", mensagem, "passagens_encontradas", "B")

    # Passagens encontrados pelo server C
    passagens_c = requests_get(SERVER_URL_C, "/passagens", mensagem, "passagens_encontradas", "C")


    # Verifica qual servidor retornou pelo menos uma passagem e adiona numa lista pra enviar ao cliente
    passagens_servidores = servidor_encontrou_passagem(passagens_a, passagens_b, passagens_c)

    return jsonify({"passagens_encontradas": passagens_servidores})

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
