from flask import Flask, request, jsonify

from utils_server_a import *
from connection import *

app = Flask(__name__)

SERVER_URL_A = "http://127.0.0.1:65433"
SERVER_URL_C = "http://127.0.0.1:65435"

# Retorna caminhos encontrados de origem a destino
@app.route('/caminhos', methods=['GET'])
def handle_caminhos():
    # Transforma mensagem do cliente em dicionário
    data = request.json

    # Pega origem e destino
    origem = data['origem']
    destino = data['destino']
    requerente = data['requerente']
    
    # Carrega grafo e encontra caminho do servidor B
    G = carregar_grafo()
    caminhos_b = encontrar_caminhos(G, origem, destino)

    # Como foi um servidor que pediu essa requisição, ele não precisa pedir a outros servidores caminhos
    # pois outro servidor ta pedindo isso a ele
    if requerente == "servidor":
        return jsonify({"caminhos_encontrados": caminhos_b})

    # Lista para armazenar caminhos encontrados por servidor A, B e C
    caminhos_servidores = []

    # Pra receber caminhos do server A e C
    caminhos_a, caminhos_c = []

    mensagem = {
        "origem": origem,
        "destino": destino,
        "requerente": "servidor"
    }



    # Aqui adiciona thread para pedir caminho do server A e C ao mesmo tempo



    # Caminhos encontrados pelo server A
    caminhos_a = requests_get(SERVER_URL_A, "/caminhos", mensagem, "caminhos_encontrados", "A")

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
    requerente = data['requerente']
    
    # Aqui vai usar para encontrar novamente caminhos novos caso algum server não tenha mais os trechos
    origem = caminho[1][0]
    destino = caminho[1][len(caminho[1]) - 1]

    # Separa cada trecho do caminho ao seu devido servidor
    trechos_server_a, trechos_server_b, trechos_server_c = desempacota_caminho_cliente(caminho)

    G = carregar_grafo()
    
    # Vê se trechos do server B ainda tão disponíveis
    comprar = verifica_trechos_escolhidos(G, trechos_server_b)


    # Aqui que a merda acontece, não posso gravar a compras dos trechos no arquivo do server B, porque se
    # o server A ou C não tiver mais os seus trechos disponíveis, não posso gravar em nenhum server.
    # Teria que verificar nos 3 server ao mesmo tempo e gravar neles ao mesmo tempo

    # Por enquanto ta o cenário perfeito, server B consegue se comunicar com A e C, e eles
    # conseguem comprar os trechos numa boa


    # Se servidor B tem os trechos ainda, envia os trechos do A e C para eles registrarem a compra tbm
    if comprar:

        # Se quem chamou o método foi um cliente, servidor precisa enviar os trechos escolhidos pelo cliente para os 
        # outros 2 servidores (caso o caminho escolhido possua algum trecho de outro servidor)

        # Se quem chamou o método foi outro servidor, só preciso registrar a compra
        if requerente == "cliente":
            mensagem = {
                "caminho": caminho,
                "cpf": cpf,
                "requerente": "servidor"
            }


            # Aqui adiciona thread para ENVIAR trechos do server B e C ao mesmo tempo


            # Se tiver algum trecho a enviar ao server A
            if trechos_server_a:

                # Resposta da compra do server A
                resposta_a, status_a = requests_post(SERVER_URL_A, "/comprar", mensagem, "resultado", "A")
                print(f"{resposta_a}")

            # Se tiver algum trecho a enviar ao server C
            if trechos_server_c:

                # Resposta da compra do server C
                resposta_c, status_c = requests_post(SERVER_URL_C, "/comprar", mensagem, "resultado", "C")
                print(f"{resposta_c}")

        # Como A e C já registrou a compra, server B registra tbm
        registra_trechos_escolhidos(G, trechos_server_b, cpf)

        return jsonify({"resultado": "Compra realizada com sucesso"}), 200

    # Se trechos do server A não tiverem mais disponíveis, nem precisa enviar os trechos do server B e C para eles
    # Aqui tem que implementar para caso B não tenha mais, ele peça pro A e C para enviar novamente seus caminhos encontrados
    # de origem a destino e devolver pro cliente novamente 

    # Por enquanto só retorna que a compra deu merda
    else:
        return jsonify({"resultado": "Caminho indisponível"}), 400

# Pra verificar compras de um cliente
@app.route('/passagens', methods=['GET'])
def handle_passagens_compradas():
    # Transforma mensagem do cliente em dicionário
    data = request.json
    
    # Pega cpf do cliente
    cpf = data['cpf']
    requerente = data['requerente']

    # Verifica se tem passagens compradas por CPF no servidor B
    passagens_b = verifica_compras_cpf(cpf)

    # Como foi um servidor que pediu essa requisição, ele não precisa pedir a outros servidores passagens
    # pois outro servidor ta pedindo isso a ele
    if requerente == "servidor":
        return jsonify({"passagens_encontradas": passagens_b})

    # Pra receber passagens do server A e C
    passagens_a, passagens_c = []

    # Lista para armazenar passagens encontrados por servidor A, B e C
    passagens_servidores = []

    mensagem = {
        "cpf": cpf,
        "requerente": "servidor"
    }


    # Aqui adiciona thread para pedir passagens do server A e C ao mesmo tempo


    # Passagens encontrados pelo server A
    passagens_a = requests_get(SERVER_URL_A, "/passagens", mensagem, "passagens_encontradas", "A")

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
