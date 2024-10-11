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

precisa_comunicacaoB = False
menssage_to_B = None
precisa_comunicacao = False
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
    global precisa_comunicacaoB
    global menssage_to_B
    #transformando em dic 
    data = request.json
    #fazendo mesmo que antes
    origem_1 = data['origem']
    destino_1 = data['destino']
    origem = cidades[int(origem_1) - 1]
    destino = cidades[int(destino_1) - 1]

    # Processo de encontrar caminhos com threading
    def tarefa_caminhos(origem, destino):
        global precisa_comunicacaoB
        global menssage_to_B
        try:
            G = carregar_grafo()
            caminhos = encontrar_caminhos(G, origem, destino)
            if not caminhos:
                print("Nenhum caminho encontrado. O cliente deve tentar outro servidor.")
                return 404
            
            return caminhos
        
        except Exception as e:
            print(f"Erro ao processar: {str(e)}")
            # precisa_comunicacao = True
            return 500


    caminhos = process_threaded_task(tarefa_caminhos, origem, destino)
    if isinstance(caminhos,(int,float)):
        precisa_comunicacaoB = True
        menssage_to_B = {
            "origem":origem_1,
            "destino":destino_1
        }

        start_time = time.time()
        timeout = 10  # tempo máximo de espera em segundos


        while B_Receive_buffer is None and (time.time() - start_time) < timeout:
            time.sleep(0.5)  # Aguardar meio segundo antes de verificar novamente

        if B_Receive_buffer is not None:
            return jsonify({"caminhos_encontrados": B_Receive_buffer['caminhos_encontrados']})
        else:
            return jsonify({"error": "Timeout: não foi possível receber os dados do servidor B."}), 504
    
    else:   
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





def start_servent(): #servent = server + client, massa né kkkkkk servente ententedeu  HAHAHAHHAHAHAHAHAHHAHAHAHAHAAHAH

    global precisa_comunicacaoB
    global B_Receive_buffer
    global menssage_to_B
    server_url = "http://127.0.0.1:65434"  # URL do servidor

    while True:
         
        # Exemplo de lógica para enviar uma solicitação
        if precisa_comunicacaoB:
            print("Iniciando comunicação com outro servidor B...")

            try:
                response = requests.get(server_url+"/caminhos", json=menssage_to_B)
                if response.status_code == 200:
                    # Processar a resposta como necessário
                    B_Receive_buffer = response.json()
                    print(f"Dados recebidos do servidor B: {B_Receive_buffer}")
                else:
                    print("Erro ao receber dados do servidor B.")
            except Exception as e:
                print(f"Erro na comunicação com o servidor B: {str(e)}")


            precisa_comunicacaoB = False  # Resetar a variável após a comunicação







if __name__ == "__main__":
    # O Flask usa `run` para iniciar o servidor HTTP
    cria_arquivo_grafo()
    threading.Thread(target=start_servent, daemon=True).start()
    app.run(host='0.0.0.0', port=65433)
    


