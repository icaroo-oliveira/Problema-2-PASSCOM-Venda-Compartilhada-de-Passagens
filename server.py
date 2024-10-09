import threading
import json
import queue
from connection import config_server, receber_mensagem, encerrar_conexao, testa_conexao, get_ip_address
from utils_server import *

#IP = get_ip_address('enp3s0f0')
IP = 'localhost'

PORTA = 65433

# Condition para controlar acesso a fila de threads (adicionar e retirar threads na fila)
condition = threading.Condition()

# Lock separado para a região crítica (acesso a arquivos e afins)
lock = threading.Lock()

# Fila para garantir a ordem de acesso das threads a região crítica (FIFO)
waiting_queue = queue.Queue()

# Thread que opera cliente individualmente
# Parâmetros ->     conexao_socket: socket da comunicação com cliente
#                   client_address: tupla contendo IP e Porta do cliente
# Retorno ->        Sem retorno
def handle_client(conexao_socket, client_address):
    try:
        print(f"Conectado a {client_address}")

        # Espera resposta do socket conexão
        data = receber_mensagem(conexao_socket)

        # Se receber algum dado, opera
        # Se não receber nenhum dado, vai pro finally e encerra conexão
        if data:
            flag, origem, destino, cpf, caminho = data.decode('utf-8').split(',', 4)

            # Thread atual
            current_thread = threading.current_thread()
            
            # Se cliente enviou flag Caminhos, servidor retorna caminhos de origem a destino
            if flag == "Caminhos":
                origem = cidades[int(origem) - 1]
                destino = cidades[int(destino) - 1]

                print(f"Recebido a flag: {flag}")
                print(f"Recebido a origem: {origem}")
                print(f"Recebido o destino: {destino}")

                # Adiciona thread a fila e verifica se ela é a primeira da fila
                adicionar_thread_fila(condition, current_thread, waiting_queue)
                
                # Região crítica - Outra thread não pode mexer no arquivo enquanto tiver carregando informação do arquivo e
                # enviando ao cliente
                with lock:
                    print(f"Thread {current_thread.name} acessando a região crítica.")

                    G = carregar_grafo()
                    caminhos = encontrar_caminhos(G, origem, destino)

                    # Nessa parte aqui, antes de enviar ao cliente, o servidor vai adicionar numa lista, os caminhos
                    # encontrados pelo Server "A", "B" e "C", e vai enviar essa lista
                    # Exemplo: [
                    #               [ "A", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ],
                    #               [ "B", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ],
                    #               [ "C", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ]
                    #          ]
                    # Logo, lista[0] = caminhos do server A; lista[1] = caminhos do server B; lista[2] = caminhos do server C
                    # Não necessariamente nessa ordem!!!!!

                    # É preciso verificar se a lista retornada pelos servidores é vazia, se for, nem adiciona na lista e nem
                    # envia ao cliente

                    # Lista de caminhos. Cada item da lista = Servidor + caminhos encontrados
                    serializa = json.dumps(caminhos)

                    mensagem = f"Caminhos_Encontrados,{serializa}"

                    # Verifica se cliente deu close() (encerrou conexão)
                    # Se não encerrou, envia os caminhos encontrados
                    teste = testa_conexao(conexao_socket, mensagem)

                    verifica_teste(teste, "Caminhos enviados com sucesso")
                    
                    # Remove thread atual da fila e notifica as outras threads
                    remover_thread_fila(condition, current_thread, waiting_queue)

            # Se cliente enviou flag Comprar, servidor retorna sucesso de compra ou novos caminhos
            elif flag == "Comprar":
                print(f"Recebido a flag: {flag}")
                print(f"Recebido o caminho: {caminho}")
                print(f"Recebido o cpf: {cpf}")

                # Uma tupla contendo lista dos servidores de cada trecho e lista de trechos (forma caminho)
                caminho = json.loads(caminho)

                # aqui ele vai desempacotar a tupla recebida e retornar 3 lista. Cada lista irá conter os trechos pertencidos
                # a cada um dos 3 servidores. Depois vai enviar as listas para cada servidor para verificar se os trechos ainda tao
                # disponíveis e se tiver, confirma compra
                
                # Primeiro item da lista = origem
                origem = caminho[1][0]

                # Ultimo item da lista = destino
                destino = caminho[1][len(caminho[1]) - 1]

                # Adiciona thread a fila e verifica se ela é a primeira da fila
                adicionar_thread_fila(condition, current_thread, waiting_queue)
                
                # Região crítica - Outra thread não pode mexer no arquivo enquanto tiver carregando informação do arquivo ou
                # gravando informação nele, e enviando ao cliente
                with lock:
                    print(f"Thread {current_thread.name} acessando a região crítica.")

                    # Pega informação atual do grafo
                    G = carregar_grafo()

                    # Verifica se caminho ainda ta disponível
                    comprar = verifica_trechos_escolhidos(G, caminho)
                    
                    # Se retornou false, caminho não ta mais disponível
                    # encontra e retorna novos caminhos para cliente (grafo atualizado)
                    if comprar == False:
                        caminhos = encontrar_caminhos(G, origem, destino)

                        # Lista de tuplas atualizada. Cada tupla = Um caminho
                        serializa = json.dumps(caminhos)

                        mensagem = f"Novos_Caminhos_Encontrados,{serializa}"

                        # Verifica se cliente deu close() (encerrou conexão)
                        # Se não encerrou, envia os novos caminhos encontrados
                        teste = testa_conexao(conexao_socket, mensagem)

                        verifica_teste(teste, "Novos caminhos enviados com sucesso")
                    
                    # Se retornou true, caminho ta disponível
                    else:
                        # Registra compra
                        registra_trechos_escolhidos(G, caminho, cpf)

                        mensagem = f"Compra_Feita,"

                        # Verifica se cliente deu close() (encerrou conexão)
                        # Se não encerrou, envia informação indicando exito na compra
                        teste = testa_conexao(conexao_socket, mensagem)

                        verifica_teste(teste, "Compra registrada com sucesso")
                    
                    # Remove thread atual da fila e notifica as outras threads
                    remover_thread_fila(condition, current_thread, waiting_queue)
            
            # Se cliente enviou flag Passagens_Compradas, servidor retorna passagens encontradas ou nenhuma passagem encontrada
            elif flag == "Passagens_Compradas":
                print(f"Recebido a flag: {flag}")
                print(f"Recebido o cpf: {cpf}")

                # Adiciona thread a fila e verifica se ela é a primeira da fila
                adicionar_thread_fila(condition, current_thread, waiting_queue)

                # Região crítica - Outra thread não pode mexer no arquivo enquanto tiver carregando informação do arquivo ou
                # gravando informação nele, e enviando ao cliente
                with lock:
                    print(f"Thread {current_thread.name} acessando a região crítica.")

                    # Pode vir vazio se não encontrou passagens no CPF
                    compras = verifica_compras_cpf(cpf)

                    # Lista de dicionários. Cada dicionário = Uma compra de determinado CPF
                    serializa = json.dumps(compras)

                    mensagem = f"Passagens_Encontradas,{serializa}"

                    # Verifica se cliente deu close() (encerrou conexão)
                    # Se não encerrou, envia informação indicando exito na compra
                    teste = testa_conexao(conexao_socket, mensagem)

                    verifica_teste(teste, "Passagens encontradas enviadas com sucesso")

                    # Remove thread atual da fila e notifica as outras threads
                    remover_thread_fila(condition, current_thread, waiting_queue)

            # Se cliente enviou flag inválida (não corresponde a nenhuma operação), 
            # servidor retorna informação referente
            else:
                print(f"Recebido a flag: {flag}")
                print("Operação não identificada.")

                mensagem = f"Flag_Invalida,"

                # Verifica se cliente deu close() (encerrou conexão)
                # Se não encerrou, envia informação indicando flag inválida recebida
                teste = testa_conexao(conexao_socket, mensagem)

                verifica_teste(teste, "Operação não identificada enviada com sucesso")

    finally:
        encerrar_conexao(conexao_socket)
        print("\nConexão encerrada. Aguardando nova conexão...\n")

def start_server():
    # Se não conseguir criar e configurar servidor, encerra programa
    server_socket = config_server(IP, PORTA)
    if server_socket is None:
        print("Erro ao iniciar o servidor. Encerrando aplicação.")
        return
    
    # Se não existir o arquivo, cria um novo
    cria_arquivo_grafo()
    
    # Retorna IP e Porta associada ao socket do servidor
    print(f"\nServidor -> IP: {server_socket.getsockname()[0]}  |  Porta: {server_socket.getsockname()[1]}\n")
    print("Aguardando conexão...")

    # Fica procurando solicitações de conexão constantemente
    while True:
        try:
            # Bloqueia a execução do programa até alguém se conectar
            # Retorna socket da conexão com cliente e informações sobre o cliente (IP e porta)
            conexao_socket, client_address = server_socket.accept()

            # Define um timeout de 10 segundos e cria uma thread para lidar com a nova conexão
            conexao_socket.settimeout(10)
            client_thread = threading.Thread(target=handle_client, args=(conexao_socket, client_address))
            client_thread.start()

        # Se não conseguir se conectar com um cliente, volta a procurar conexões
        except (OSError, Exception) as e:
            print(f"Erro ao aceitar conexão: {e}.")

if __name__ == "__main__":
    start_server()
