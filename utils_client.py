import heapq
import networkx as nx

# Cidades disponíveis no sistema
CIDADES = ("Cuiabá", "Goiânia", "Campo Grande", "Belo Horizonte", "Vitória", 
            "São Paulo", "Rio de Janeiro", "Curitiba", "Florianópolis", "Porto Alegre")

# Constante que determina valor de 100km do servidor A
VALOR_100_KM_A = 115

# Constante que determina valor de 100km do servidor B
VALOR_100_KM_B = 125

# Constante que determina valor de 100km do servidor B
VALOR_100_KM_C = 135

# Preço de cada servidor por 100km
VALOR_SERVIDOR = {"A": VALOR_100_KM_A, "B": VALOR_100_KM_B, "C": VALOR_100_KM_C}

# Função para calcular valor de um trecho, a depender do servidor
# Parâmetros ->     dist_trecho: quilometragem total de um trecho
#                   valor_servidor: preço do servidor por 100km
# Retorno ->        total: preço daquele trecho
def valor_trecho(dist_trecho, valor_servidor):
    total = (dist_trecho / 100) * valor_servidor
    return round(total, 2)

# Função para iniciar grafo temporário do cliente
# Parâmetros ->     Sem parâmetros
# Retorno ->        G: grafo temporário do cliente

# Assim que o cliente abrir a aplicação, esse grafo temporário é criado para receber 
# a lista com os caminhos encontrados pelos servidores
# O campo "servidores" de cada trecho, é uma lista que vai guardar qual servidor achou caminho com o atual trecho
# Logo essa lista pode ter até 3 itens: "A", "B" e "C"
# Primordialmente ela é vazia pois servidor ainda não retornou nenhum caminho, obvio
def inicia_grafo():
    # Criando um novo grafo
    G = nx.DiGraph()

    # Caminhos de Cuiabá
    G.add_edge("Cuiabá", "Goiânia", distancia=890, servidores=[])
    G.add_edge("Cuiabá", "Campo Grande", distancia=700, servidores=[])

    # Caminhos de Goiânia
    G.add_edge("Goiânia", "Cuiabá", distancia=890, servidores=[])
    G.add_edge("Goiânia", "Campo Grande", distancia=840, servidores=[])
    G.add_edge("Goiânia", "Belo Horizonte", distancia=890, servidores=[])

    # Caminhos de Campo Grande
    G.add_edge("Campo Grande", "Cuiabá", distancia=700, servidores=[])
    G.add_edge("Campo Grande", "Goiânia", distancia=840, servidores=[])
    G.add_edge("Campo Grande", "Belo Horizonte", distancia=1250, servidores=[])
    G.add_edge("Campo Grande", "São Paulo", distancia=980, servidores=[])
    G.add_edge("Campo Grande", "Curitiba", distancia=1000, servidores=[])

    # Caminhos de Belo Horizonte
    G.add_edge("Belo Horizonte", "Goiânia", distancia=890, servidores=[])
    G.add_edge("Belo Horizonte", "Vitória", distancia=510, servidores=[])
    G.add_edge("Belo Horizonte", "Campo Grande", distancia=1250, servidores=[])
    G.add_edge("Belo Horizonte", "São Paulo", distancia=585, servidores=[])
    G.add_edge("Belo Horizonte", "Rio de Janeiro", distancia=440, servidores=[])

    # Caminhos de Vitória
    G.add_edge("Vitória", "Belo Horizonte", distancia=510, servidores=[])
    G.add_edge("Vitória", "Rio de Janeiro", distancia=520, servidores=[])

    # Caminhos de São Paulo
    G.add_edge("São Paulo", "Belo Horizonte", distancia=585, servidores=[])
    G.add_edge("São Paulo", "Campo Grande", distancia=980, servidores=[])
    G.add_edge("São Paulo", "Rio de Janeiro", distancia=440, servidores=[])
    G.add_edge("São Paulo", "Curitiba", distancia=400, servidores=[])

    # Caminhos de Rio de Janeiro
    G.add_edge("Rio de Janeiro", "Vitória", distancia=520, servidores=[])
    G.add_edge("Rio de Janeiro", "Belo Horizonte", distancia=440, servidores=[])
    G.add_edge("Rio de Janeiro", "São Paulo", distancia=440, servidores=[])

    # Caminhos de Curitiba
    G.add_edge("Curitiba", "Campo Grande", distancia=1000, servidores=[])
    G.add_edge("Curitiba", "São Paulo", distancia=400, servidores=[])
    G.add_edge("Curitiba", "Florianópolis", distancia=300, servidores=[])

    # Caminhos de Florianópolis
    G.add_edge("Florianópolis", "Curitiba", distancia=300, servidores=[])
    G.add_edge("Florianópolis", "Porto Alegre", distancia=460, servidores=[])

    # Caminhos de Porto Alegre
    G.add_edge("Porto Alegre", "Florianópolis", distancia=460, servidores=[])

    return G

# Função para preencher grafo temporário do cliente com os caminhos encontrados pelos servidores
# Parâmetros ->     lista: contém caminhos encontrados pelos servidores
# Retorno ->        G: grafo temporário do cliente (já preenchido)

# Quando cliente receber a lista com os caminhos encontrados pelo servidores, ele vai alimentar o grafo temporário
# Exemplo: [
#               [ "A", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ],
#               [ "B", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ],
#               [ "C", ["curitiba", "bh", "rj", "sao paulo"], ["curitiba", "cuiabá", "sao paulo"] ]
#          ]
def preenche_grafo(lista):
    G = inicia_grafo()

    # tamanho da lista geral - itera sobre os caminhos de todos os servidores
    for i in range(len(lista)):
        # Nome do servidor
        servidor = lista[i][0]

        # Quantidade de caminhos retornado por um dos server. Começa em 1 porque o item 0 é o nome do servidor
        for j in range(1, len(lista[i])):
            
            # tamanho de um dos caminhos de um servidor
            for k in range(len(lista[i][j]) - 1):
                trecho = (lista[i][j][k], lista[i][j][k + 1])
                
                # Como um servidor pode retornar caminhos com trechos iguais, preciso verificar se determinado trecho
                # já guardou que ele foi retornado pelo servidor em questão
                # Exemplo: O caminho 1, do servidor A tem o trecho rj -> são paulo, na primeira iteração já foi guardado
                # "A" em sua lista. Porém o caminho 2 do servidor A também tem o trecho rj -> são paulo, logo não preciso
                # guardar "A" novamente!!!
                if servidor not in G[trecho[0]][trecho[1]]['servidores']:
                    G[trecho[0]][trecho[1]]['servidores'].append(servidor)
    
    return G

# Função para encontrar os 5 caminhos mais curtos e 5 caminhos mais baratos
# Parâmetros ->     grafo: grafo temporário do cliente
#                   cidade_inicial: cidade origem
#                   cidade_fim: cidade destino
#                   servidor_conectado_nome: nome do servidor conectado pelo cliente (determina prioridade)
# Retorno ->        caminhos_ordenados_distancia: lista com 5 caminhos mais curtos
#                   caminhos_ordenados_valor: lista com 5 caminhos mais baratos

# Com o grafo já alimentado, cliente vai encontrar os 5 caminhos mais curtos e os 5 caminhos mais baratos
# Como grafo contém trecho de servidor A, B e C, os caminhos encontrados vão ter trechos de servidores misturados
# Critério para caso mais de um servidor tenha encontrado determinado trecho:

# 1° Caminhos mais curtos
# Caso um trecho tenha sido retornado por mais de um servidor, prefência será do servidor atualmente conectado pelo cliente.
# Se tal servidor não encontrou o trecho, preferência será pelo servidor mais barato, pois a distancia é a mesma para todos

# 2° Caminhos mais baratos
# Caso um trecho tenha sido retornado por mais de um servidor, prefência será pelo servidor mais barato

# ps: Retorna uma tupla com 2 listas: 1 com os 5 caminhos mais curtos, 1 com os 5 caminhos mais baratos
# ps: Cada uma das lista é uma lista de tuplas onde ,  1° item da tupla = distancia total do caminho (lista 1°) ou valor total do caminho (lista 2°)
#                                                      2° item da tupla = distancia total do caminho (lista 1°) ou valor total do caminho (lista 2°)
#                                                      3° item da tupla = lista com os servidores de cada trecho
#                                                      4° item da tupla = lista com os trechos (origem à destino)

# ex da lista 1° - distancia item 0: [
#                                       (223, 300, ["A", "B"], ["curitiba", "cuiabá", "sao paulo"]),
#                                       (567, 700, ["A", "C", "A"], ["curitiba", "bh", "rj", "sao paulo"]),
#                                       ... mais 1 pra fechar 3 (ou nao, se tiver menos que 3)  
#                                    ]

# ex da lista 2° - valor item 0: [
#                                   (300, 223, ["A", "B"], ["curitiba", "cuiabá", "sao paulo"]),
#                                   (700, 567, ["A", "C", "A"], ["curitiba", "bh", "rj", "sao paulo"]),
#                                   ... mais 1 pra fechar 3 (ou nao, se tiver menos que 3)  
#                                ]
def encontrar_caminhos(grafo, cidade_inicial, cidade_fim, servidor_conectado_nome):
    # Lista dos 5 caminhos mais curtos
    caminhos_distancia = []

    # Lista dos 5 caminhos mais baratos
    caminhos_valor = []
    
    # Retorna todos os caminhos possíveis entre origem e destino
    for path in nx.all_simple_paths(grafo, source=cidade_inicial, target=cidade_fim):
        caminho_valido = True

        # Lista que indica a qual servidor pertence o trecho retornado (lista a depender do valor)
        servidores_valor = []

        # Lista que indica a qual servidor pertence o trecho retornado (lista a depender da distancia)
        servidores_distancia = []

        # Variável que irá guardar o valor total de um caminho (lista a depender do valor)
        valor_caminho_valor = 0

        # Variável que irá guardar o valor total de um caminho (lista a depender da distancia)
        valor_caminho_distancia = 0

        # Variável que irá guardar a distancia total de um caminho
        dist_caminho = 0

        # Itera sobre o caminho encontrado
        for i in range(len(path) - 1):
            trecho = (path[i], path[i + 1])

            # Lista com os servidores que retornaram esse trecho em questão
            lista_servers = grafo[trecho[0]][trecho[1]]['servidores']

            # Verifica se trecho em questão do caminho encontrado não foi retornado por nenhum servidor
            if not lista_servers:
                caminho_valido = False
                break
            
            # Servidor prioridade da lista a depender do valor e o valor desse servidor
            server_prioridade_valor, valor_servidor_valor = verifica_servidor_prioridade(lista_servers, servidor_conectado_nome, False)

            # Servidor prioridade da lista a depender da distancia e o valor desse servidor
            server_prioridade_distancia, valor_servidor_distancia = verifica_servidor_prioridade(lista_servers, servidor_conectado_nome, True)

            # Informo a qual servidor esse trecho pertence (lista a depender do valor)
            servidores_valor.append(server_prioridade_valor)

            # Informo a qual servidor esse trecho pertence (lista a depender da distancia)
            servidores_distancia.append(server_prioridade_distancia)

            # Pego a distancia dessse trecho
            dist_trecho = grafo[trecho[0]][trecho[1]]['distancia']

            # Somo valor desse trecho ao valor total do caminho (lista a depender do valor)
            valor_caminho_valor += valor_trecho(dist_trecho, valor_servidor_valor)

            # Somo valor desse trecho ao valor total do caminho (lista a depender da distancia)
            valor_caminho_distancia += valor_trecho(dist_trecho, valor_servidor_distancia)

            # Somo distancia desse trecho a distancia total do caminho
            dist_caminho += dist_trecho

        if caminho_valido:
            # Organiza os caminhos em fila de prioridade (menor ao maior) a depender da distancia
            heapq.heappush(caminhos_distancia, (dist_caminho, valor_caminho_distancia, servidores_distancia, path))

            # Organiza os caminhos em fila de prioridade (menor ao maior) a depender do valor
            heapq.heappush(caminhos_valor, (valor_caminho_valor, dist_caminho, servidores_valor, path))

    # Obtém os 5 melhores caminhos (se existirem)
    caminhos_ordenados_distancia = heapq.nsmallest(5, caminhos_distancia)
    
    caminhos_ordenados_valor = heapq.nsmallest(5, caminhos_valor)
    
    return caminhos_ordenados_distancia, caminhos_ordenados_valor

# Função para verificar prioridade de um servidor sobre um trecho
# Parâmetros ->     lista_servers: lista com servidores que retornaram trecho em questão
#                   servidor_conectado_nome: nome do servidor conectado pelo cliente (determina prioridade)
#                   flag: indica se servidor conectado pelo cliente deve ter prioridade
# Retorno ->        servidor_prioridade: nome do servidor com prioridade sobre o trecho
#                   VALOR_SERVIDOR: valor do km do servidor prioritário

# Se flag for True (lista a depender da distancia), primeiro verifica se o servidor conectado 
# pelo cliente retornou tal trecho, se não retornou ou se flag for False, volta a prioridade de servidor mais barato
def verifica_servidor_prioridade(lista_servers, servidor_conectado_nome, flag):
    if flag:
        if servidor_conectado_nome in lista_servers:
            return servidor_conectado_nome, VALOR_SERVIDOR[servidor_conectado_nome]
    
    # Ordenando o dicionário pelo menor valor (primeiro item será o servidor mais barato e por ae vai)
    valor_servidor_ordenado = dict(sorted(VALOR_SERVIDOR.items(), key=lambda item: item[1]))

    # Verifica qual servidor retornou determinado trecho dando preferência ao mais barato
    for servidor_prioridade in valor_servidor_ordenado:

        # Se o servidor estiver na lista, retorna o servidor e seu valor por km
        if servidor_prioridade in lista_servers:
            return servidor_prioridade, VALOR_SERVIDOR[servidor_prioridade]