from utils_client import *
from interface import *
from connection import *

SERVERS_URLS = (SERVER_URL_A, SERVER_URL_B, SERVER_URL_C)

NOMES_SERVIDORES = ("A", "B", "C")

# Guarda url do servidor escolhido do cliente
servidor_conectado_url = None

# Guarda nome do servidor escolhido do cliente
servidor_conectado_nome = None

def start_client():
    while True:
        clear_terminal()

        escolha2 = escolhe_servidor()

        if escolha2 == '0':
            break
        
        clear_terminal()

        # Define server a se conectar a depender da resposta do cliente
        servidor_conectado_url = SERVERS_URLS[int(escolha2) - 1]
        servidor_conectado_nome = NOMES_SERVIDORES[int(escolha2) - 1]

        sair = 0
        menu = 0

        while True:
            # Escolhe entre comprar uma passagem, ver passagens compradas em um CPF ou sair do programa
            escolha = mostrar_menu_principal(servidor_conectado_nome)

            if escolha == '0' or escolha == '3':
                break

            sair = 0
            menu = 0

            clear_terminal()
            
            # Se escolheu comprar uma passagem
            if escolha == '1':
                while True:
                    origem, destino = selecionar_cidades(CIDADES)
                    
                    # Encerra aplicação
                    if origem == "0" or destino == "0":
                        sair = 1
                        break

                    # Volta pro menu principal
                    if origem == "100" or destino == "100":
                        clear_terminal()
                        break

                    origem = CIDADES[int(origem) - 1]
                    destino = CIDADES[int(destino) - 1]
                    
                    mensagem = {
                        "origem": origem,
                        "destino": destino
                    }

                    # Solicita que server atual retorne caminhos de Origem a Destino
                    caminhos = requests_get(servidor_conectado_url, "/caminhos_cliente", mensagem, "caminhos_encontrados", servidor_conectado_nome, 15)
                    
                    # Se não conseguiu requisição, volta a escolha de origem e destino
                    if caminhos is None:
                        continue

                    # Verifica se servidor achou algum caminho de origem à destino, se achou
                    # exibe caminhos e aguarda escolha do usuário entre voltar ao menu principal, sair do programa
                    # ou tentar comprar um caminho
                    if caminhos:
                        G = preenche_grafo(caminhos)
                        caminhos_ordenados_distancia, caminhos_ordenados_valor = encontrar_caminhos(G, origem, destino, servidor_conectado_nome)

                        # Caso cliente não consiga se conectar, enviar ou receber dados do servidor, 
                        # ele escolhe caminho e cpf de novo e tenta conectar e enviar ou receber os dados novamente
                        while True:
                            escolha, cpf = selecionar_caminho(origem, destino, caminhos_ordenados_distancia, caminhos_ordenados_valor)

                            # Encerra aplicação
                            if escolha == "0" or cpf == "0":
                                sair = 1
                                break
                            
                            # Volta ao menu principal
                            if escolha == "100" or cpf == "100":
                                menu = 1

                                clear_terminal()
                                break

                            mensagem = {
                                "caminho": escolha,
                                "cpf": cpf
                            }

                            # Solicita que server atual afetue compra do caminho escolhido
                            resposta, status = requests_post(servidor_conectado_url, "/comprar_cliente", mensagem, "resultado", servidor_conectado_nome, 25)
                            if resposta is None and status is None:
                                continue
                            
                            # Se não der merda, sai do loop
                            break
                        
                        # se escolheu sair ou ir pro menu principal, sai do while e volta ao menu principal ou encerra programa
                        if sair or menu:
                            break

                        # Informa mensagem recebida pelo servidor
                        imprime_divisoria()
                        print(resposta)
                        imprime_divisoria()

                        sleep_clear(5)
                        
                        # Se compra foi feita, volta ao menu principal
                        if status == 200:
                            break

                        # Se caminho não tava mais disponível, volta a escolha de origem e destino
                        
                    # Caso servidor retorne nenhum caminho, volta a escolha de origem e destino
                    else:
                        imprime_divisoria()
                        print(f"Nenhum caminho disponível de {origem} para {destino}")
                        imprime_divisoria()

                        sleep_clear(5)
            
            # Se escolheu verificar passagens compradas em um CPF
            elif escolha == '2':
                # Caso cliente não consiga se conectar, enviar ou receber dados do servidor, 
                # ele escolhe cpf de novo e tenta conectar e enviar ou receber os dados novamente
                while True:
                    cpf = verificar_passagens_compradas()
                    
                    # Encerra aplicação
                    if cpf == "0":
                        sair = 1
                        break

                    # Volta pro menu principal
                    if cpf == "100":
                        menu = 1
                        
                        clear_terminal()
                        break
                                
                    mensagem = {
                        "cpf": cpf
                    }

                    # Solicita que server atual retorne passagens compradas pelo cliente (cpf)
                    passagens = requests_get(servidor_conectado_url, "/passagens_cliente", mensagem, "passagens_encontradas", servidor_conectado_nome, 15)
                    if passagens is None:
                        continue
                    
                    # Se não der merda, sai do loop
                    break
                
                # Volta pro menu principal
                if menu:
                    continue
                
                # Fecha o programa
                if sair:
                    break
            
                # Lista de dicionários. Cada dicionário = Uma compra de determinado CPF
                # Se servidor encontrou passagens compradas no CPF, 
                # exibe e aguarda escolha do usuário entre voltar ao menu principal ou sair do programa
                if passagens:
                    escolha = exibe_compras_cpf(cpf, passagens)
                    
                    if escolha == '0':
                        break

                # Se servidor não encontrou passagens compradas no CPF, volta ao menu principal automaticamente
                else:
                    imprime_divisoria()
                    print(f"Não existem passagens compradas para CPF: {cpf}")
                    imprime_divisoria()

                    sleep_clear(5)
            
            # Encerra aplicação
            if sair:
                break
        
        if escolha == '0' or sair:
            break

    clear_terminal()
    imprime_divisoria()
    print("Até a próxima!")
    imprime_divisoria()

if __name__ == "__main__":
    start_client()