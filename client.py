from utils_client import *
from interface import mostrar_menu_principal, selecionar_cidades, selecionar_caminho, verificar_passagens_compradas, exibe_compras_cpf
import requests

server_url = "http://127.0.0.1:65433"
#ou http://localhost:65433


def start_client():
    while True:
        # Escolhe entre comprar uma passagem, ver passagens compradas em um CPF ou sair do programa
        escolha = mostrar_menu_principal()

        if escolha == '0':
            break

        sair = 0
        menu = 0
        
        # Se escolheu comprar uma passagem
        if escolha == '1':
            # Caso cliente não consiga se conectar, enviar ou receber dados ao servidor, 
            # ele escolhe origem e destino de novo e tenta conectar e enviar ou receber os dados novamente
            while True:
                origem, destino = selecionar_cidades(cidades)
                
                # Encerra aplicação
                if origem == "0" or destino == "0":
                    sair = 1
                    break

                # Volta pro menu principal
                if origem == "100" or destino == "100":
                    menu = 1
                    
                    clear_terminal()
                    break
                

                mensagem = {
                    "origem":origem,
                    "destino":destino
                }

               
            
                #usando get, para encontrar os caminhos de {origem} a {destino}
                response = requests.get(server_url+"/caminhos", json=mensagem)


                if response.status_code == 200:
                    print("Caminhos encontrados:", response.json()["caminhos_encontrados"])
                else:
                    print("Erro:", response.status_code)
                break
            
            # Volta pro menu principal
            if menu:
                continue
            
            # Fecha o programa
            if sair:
                break

            
            caminhos = response.json()["caminhos_encontrados"]

            while True:
                # Verifica se servidor achou algum caminho de origem à destino, se achou
                # exibe caminhos e aguarda escolha do usuário entre voltar ao menu principal, sair do programa
                # ou tentar comprar um caminho
                if caminhos:
                    # Caso cliente não consiga se conectar, enviar ou receber dados do servidor, 
                    # ele escolhe caminho e cpf de novo e tenta conectar e enviar ou receber os dados novamente
                    while True:
                        escolha, cpf = selecionar_caminho(cidades, origem, destino, caminhos)

                        # Encerra aplicação
                        if escolha == "0" or cpf == "0":
                            sair = 1
                            break
                        
                        # Volta ao menu principal
                        if escolha == "100" or cpf == "100":
                            menu = 1

                            clear_terminal()
                            break


                        caminho = caminhos[int(escolha)-1]

                        mensagem = {
                            "caminho":caminho,"cpf":cpf
                        }

                        
                        response = requests.post(server_url+"/caminhos", json=mensagem)                       
                        break
                    
                    # se escolheu sair ou ir pro menu principal, sai do while e volta ao menu principal ou encerra programa
                    if sair or menu:
                        break


                    print(response.json()["resultado"])
                    
                    
                  
                # Caso servidor retorne nenhum caminho, volta ao menu principal automaticamente
                else:
                    imprime_divisoria()
                    print(f"Nenhum caminho disponível de {cidades[int(origem)-1]} para {cidades[int(destino)-1]}")
                    imprime_divisoria()

                    sleep_clear(5)
                    break
            
            # Encerra aplicação
            if sair:
                break
        
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
                    "cpf":cpf
                }

                
                response = requests.get(server_url+"/passagens", json=mensagem)
                break
            
            # Volta pro menu principal
            if menu:
                continue
            
            # Fecha o programa
            if sair:
                break


            passagens = response.json()["passagens_encontradas"]
            print(passagens)
           
            # Lista de dicionários. Cada dicionário = Uma compra de determinado CPF
            # Se servidor encontrou passagens compradas no CPF, 
            # exibe e aguarda escolha do usuário entre voltar ao menu principal ou sair do programa
            if passagens:
                escolha = exibe_compras_cpf(cpf, passagens)
                
                if escolha == '0':
                    break

                clear_terminal()

            # Se servidor não encontrou passagens compradas no CPF, volta ao menu principal automaticamente
            else:
                imprime_divisoria()
                print(f"Não existem passagens compradas para CPF: {cpf}")
                imprime_divisoria()

                sleep_clear(5)
   
    imprime_divisoria()
    print("Até a próxima!")
    imprime_divisoria()

if __name__ == "__main__":
    start_client()