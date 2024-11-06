import time
import os
import platform

# Função para limpar terminal (reconhece qual SO utilizado)
# Parâmetros ->     Sem parâmetros
# Retorno ->        Sem retorno
def clear_terminal():
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

# Função para limpar terminal após n segundos
# Parâmetros ->     segundos: segundos que o programa deve congelar
# Retorno ->        Sem retorno
def sleep_clear(segundos):
    time.sleep(segundos)
    clear_terminal()

# Função para melhorar frontend
# Parâmetros ->     Sem parâmetros
# Retorno ->        Sem retorno
def imprime_divisoria():
    print("\n" + "=" * 120 + "\n")

# Função que exibe em tela servidores disponíveis para se conectar
# Parâmetros ->     Sem parâmetros
# Retorno ->        escolha: escolha do cliente
def escolhe_servidor():
    imprime_divisoria()
    
    while True:
        escolha = input("1- Servidor A\n2- Servidor B\n3- Servidor C\n\n0- Encerrar programa\n\n>>> ")
        if escolha in ['0', '1', '2', '3']:
            break
        print("\nEntrada inválida.\n")
    
    return escolha

# Função que exibe em tela menu principal e suas opções
# Parâmetros ->     nome_servidor: nome do servidor escolhio pelo cliente
# Retorno ->        escolha: escolha do cliente
def mostrar_menu_principal(nome_servidor):
    imprime_divisoria()
    print(f"\t\t\t\tSistema de Vendas de Passagens - Servidor {nome_servidor}")
    imprime_divisoria()

    while True:
        escolha = input("1- Comprar\n2- Minhas compras\n3- Mudar servidor\n0- Encerrar programa\n\n>>> ")
        if escolha in ['0', '1', '2', '3']:
            break
        print("\nEntrada inválida.\n")
    
    return escolha

# Função que exibe em tela menu de escolha de origem e destino
# Parâmetros ->     cidades: lista de cidades disponíneis no sistema
# Retorno ->        origem: cidade origem escolhida pelo cliente
#                   destino: cidade destino escolhida pelo cliente
def selecionar_cidades(cidades):
    imprime_divisoria()
    print("Cidades disponíveis:\n")
    for i, cidade in enumerate(cidades):
        print(f"{i+1}- {cidade}")
    print("\n0- Encerrar programa\n100- Menu\n")
    
    while True:
        origem = input("Escolha o número referente à cidade origem: ")
        if origem.isdigit() and (0 <= int(origem) <= 10 or int(origem) == 100):
            break
        print("Entrada inválida.")
    
    if origem in ["0", "100"]:
        return origem, None

    while True:
        destino = input("Escolha o número referente à cidade destino: ")
        if destino.isdigit() and (0 <= int(destino) <= 10 or int(destino) == 100) and origem != destino:
            break
        print("Entrada inválida.")
    
    return origem, destino

# Função que exibe em tela caminhos encontrados de origem a destino
# Parâmetros ->     origem: cidade origem escolhida pelo cliente
#                   destino: cidade destino escolhida pelo cliente
#                   caminhos_ordenados_distancia: lista de caminhos encontrados (a depender da distancia)
#                   caminhos_ordenados_valor: lista de caminhos encontrados retornados pelo servidor (a depender do valor)
# Retorno ->        path: caminho escolhido pelo cliente
#                   cpf: cpf do cliente
def selecionar_caminho(origem, destino, caminhos_ordenados_distancia, caminhos_ordenados_valor):
    imprime_divisoria()
    
    # Lista unificada para armazenar os caminhos - Junta as 2 listas para melhorar identificação
    # da escolha do caminho pelo cliente
    caminhos_unificados = []

    print(f"Trechos de {origem} para {destino}:\n")

    print("Caminhos mais curtos: ")
    for dist, valor, nome_servidor, path in caminhos_ordenados_distancia:
        caminhos_unificados.append((dist, valor, nome_servidor, path))
        print(f"{len(caminhos_unificados)}. Caminho: {' -> '.join(path)} | {dist}km | R$ {valor}")
        print(f"{len(caminhos_unificados)}. Servidores: {' -> '.join(nome_servidor)}\n")

    print("Caminhos mais baratos: ")
    for valor, dist, nome_servidor, path in caminhos_ordenados_valor:
        caminhos_unificados.append((valor, dist, nome_servidor, path))
        print(f"{len(caminhos_unificados)}. Caminho: {' -> '.join(path)} | {dist}km | R$ {valor}")
        print(f"{len(caminhos_unificados)}. Servidores: {' -> '.join(nome_servidor)}\n")
    
    print("0- Encerrar programa\n100- Menu\n")

    while True:
        escolha = input("Escolha um caminho: ")
        if escolha.isdigit() and (0 <= int(escolha) <= len(caminhos_unificados) or int(escolha) == 100):
            break
        print("Entrada inválida.")

    if escolha in ["0", "100"]:
        return escolha, None
    
    while True:
        cpf = input("Digite seu CPF para registro da compra (apenas número maior que 100): ")
        if cpf.isdigit() and (int(cpf) == 0 or int(cpf) >= 100):
            break
        print("Entrada inválida.")

    # EX: (223, 300, ["A", "B"], ["curitiba", "cuiabá", "sao paulo"])
    caminho = caminhos_unificados[int(escolha) - 1]

    # EX: (["A", "B"], ["curitiba", "cuiabá", "sao paulo"])
    # Retorno ao servidor apenas os trechos e a quem pertence cada trecho
    path = (caminho[2], caminho[3])
    
    return path, cpf

# Função que exibe em tela menu de escolha de cpf para ter acesso as passagens compradas
# Parâmetros ->     Sem parâmetros
# Retorno ->        cpf: cpf enviado pelo cliente
def verificar_passagens_compradas():
    imprime_divisoria()
    print("0- Encerrar programa\n100- Menu\n")

    while True:
        cpf = input("Digite seu CPF para consultar passagens compradas (apenas número maior que 100): ")
        if cpf.isdigit() and (int(cpf) == 0 or int(cpf) >= 100):
            break
        print("Entrada inválida.")
    
    return cpf

# Função que exibe em tela compras de passagens encontradas de um CPF
# Parâmetros ->     cpf: cpf do cliente
#                   passagens: lista de passagens de um cliente
# Retorno ->        escolha: entrada do cliente entre menu principal (100) ou encerrar programa (0)

# Recebe essa estrutura, exemplo
#    [
#       [ 
#           "A",
#           {'trechos': [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ], 'assentos': [1, 3], 'distancia': 1234, 'valor': 1000},
#           {'trechos': [ ('berlim', 'sao paulo'), ('salvador', 'fsa'), ('serrinha', 'bomfim') ], 'assentos': [3, 2, 1], 'distancia': 1234, 'valor': 23954},      
#       ],

#       [ 
#           "B",
#           {'trechos': [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ], 'assentos': [1, 3], 'distancia': 1234, 'valor': 1000},
#           {'trechos': [ ('berlim', 'sao paulo'), ('salvador', 'fsa'), ('serrinha', 'bomfim') ], 'assentos': [3, 2, 1], 'distancia': 1234, 'valor': 23954},      
#       ],
#       
#       [ 
#           "C",
#           {'trechos': [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ], 'assentos': [1, 3], 'distancia': 1234, 'valor': 1000},
#           {'trechos': [ ('berlim', 'sao paulo'), ('salvador', 'fsa'), ('serrinha', 'bomfim') ], 'assentos': [3, 2, 1], 'distancia': 1234, 'valor': 23954},      
#       ]
#   ]

def exibe_compras_cpf(cpf, passagens):
    imprime_divisoria()
    print(f"Compras do CPF {cpf}: \n")

    # Itera sobre a lista toda
    for i in range(len(passagens)):
        print(f"*Servidor {passagens[i][0]}*")

        # Itera sobre um item da lista = todas as compras em um servidor
        # [1:] ignora primeiro item da lista -> nome do servidor que retornou as passagens da lista
        for j, compra in enumerate(passagens[i][1:], 1):
            print(f"Compra {j} - {compra['distancia']}km | R$ {compra['valor']}")
            
            # Itera sobre os trechos de uma compra dentre as n compras de um servidor
            for k, (origem, destino) in enumerate(compra['trechos']):
                print(f"{k+1}.Trecho {origem} -> {destino} | Assento: {compra['assentos'][k]}")
            
            print()

    while True:
        escolha = input("0- Encerrar programa\n100- Menu\n\n>>> ")
        if escolha in ['0', '100']:
            break
        print("Entrada inválida.")
    
    return escolha