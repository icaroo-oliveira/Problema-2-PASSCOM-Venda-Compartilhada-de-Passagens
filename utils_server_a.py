import heapq
import json
import networkx as nx

ARQUIVO_GRAFO = 'grafo_A.json'
ARQUIVO_PASSAGENS_COMPRADAS = 'passagens_A.json'

# Constante que determina valor de 100km do servidor
VALOR_100_KM = 115

nomes_servidores = ["A", "B", "C"]

# Função para calcular valor de um trecho
# Parâmetros ->     km: quilometragem total de um trecho
# Retorno ->        total: preço daquele trecho
def valor_trecho(km):
    total = (km / 100) * VALOR_100_KM
    return round(total, 2)

# Função para quando abrir servidor, carregar ou criar o grafo
def cria_arquivo_grafo():
    # Carregando o grafo a partir do arquivo JSON
    try:
        G = carregar_grafo()
        print("Grafo carregado com sucesso.")
    
    except FileNotFoundError:
        print("Arquivo não encontrado. Criando um novo grafo.")
        
        # Criando um novo grafo e salvando
        G = nx.DiGraph()

        # Caminhos de Cuiabá
        G.add_edge("Cuiabá", "Goiânia", distancia=890, assentos=3, cpf=[])
        G.add_edge("Cuiabá", "Campo Grande", distancia=700, assentos=3, cpf=[])
        
        # Caminhos de Goiânia
        G.add_edge("Goiânia", "Cuiabá", distancia=890, assentos=3, cpf=[])
        G.add_edge("Goiânia", "Campo Grande", distancia=840, assentos=3, cpf=[])
        G.add_edge("Goiânia", "Belo Horizonte", distancia=890, assentos=3, cpf=[])

        # Caminhos de Campo Grande
        G.add_edge("Campo Grande", "Cuiabá", distancia=700, assentos=3, cpf=[])
        G.add_edge("Campo Grande", "Goiânia", distancia=840, assentos=3, cpf=[])
        G.add_edge("Campo Grande", "Belo Horizonte", distancia=1250, assentos=3, cpf=[])
        G.add_edge("Campo Grande", "São Paulo", distancia=980, assentos=3, cpf=[])
        G.add_edge("Campo Grande", "Curitiba", distancia=1000, assentos=3, cpf=[])

        # Caminhos de Belo Horizonte
        G.add_edge("Belo Horizonte", "Goiânia", distancia=890, assentos=3, cpf=[])
        G.add_edge("Belo Horizonte", "Vitória", distancia=510, assentos=3, cpf=[])
        G.add_edge("Belo Horizonte", "Campo Grande", distancia=1250, assentos=3, cpf=[])
        G.add_edge("Belo Horizonte", "São Paulo", distancia=585, assentos=3, cpf=[])
        G.add_edge("Belo Horizonte", "Rio de Janeiro", distancia=440, assentos=3, cpf=[])

        # Caminhos de Vitória
        G.add_edge("Vitória", "Belo Horizonte", distancia=510, assentos=3, cpf=[])
        G.add_edge("Vitória", "Rio de Janeiro", distancia=520, assentos=3, cpf=[])

        # Caminhos de São Paulo
        G.add_edge("São Paulo", "Belo Horizonte", distancia=585, assentos=3, cpf=[])
        G.add_edge("São Paulo", "Campo Grande", distancia=980, assentos=3, cpf=[])
        G.add_edge("São Paulo", "Rio de Janeiro", distancia=440, assentos=3, cpf=[])
        G.add_edge("São Paulo", "Curitiba", distancia=400, assentos=3, cpf=[])

        # Caminhos de Rio de Janeiro
        G.add_edge("Rio de Janeiro", "Vitória", distancia=520, assentos=3, cpf=[])
        G.add_edge("Rio de Janeiro", "Belo Horizonte", distancia=440, assentos=3, cpf=[])
        G.add_edge("Rio de Janeiro", "São Paulo", distancia=440, assentos=3, cpf=[])

        # Caminhos de Curitiba
        G.add_edge("Curitiba", "Campo Grande", distancia=1000, assentos=3, cpf=[])
        G.add_edge("Curitiba", "São Paulo", distancia=400, assentos=3, cpf=[])
        G.add_edge("Curitiba", "Florianópolis", distancia=300, assentos=3, cpf=[])

        # Caminhos de Florianópolis
        G.add_edge("Florianópolis", "Curitiba", distancia=300, assentos=3, cpf=[])
        G.add_edge("Florianópolis", "Porto Alegre", distancia=460, assentos=3, cpf=[])

        # Caminhos de Porto Alegre
        G.add_edge("Porto Alegre", "Florianópolis", distancia=460, assentos=3, cpf=[])

        # Estrutura é parecida com isso
        # { 
        #   ("São Paulo", "Rio de Janeiro") : {'distancia': 980, 'assentos': 3, 'cpf': [], 'valor': 1127},
        #   ("Vitória", "Curitiba") : {'distancia': 34, 'assentos': 3, 'cpf': [], 'valor': 39,1},
        #   ...
        # }

        # É um dicionário geral que armazena todas as conexões (grafo)
        # As chaves desse dicionário são tuplas que armazenam a v1 e v2 (cidades com conexão)
        # Os valores dessas chaves são dicionários, onde as chaves serão as distancias, assentos e cpf. Os valores
        # dessas chaves são as informações desses dados, onde cpf é uma lista que guarda cpf's que compraram
        # um assento do trecho (ou seja, lista[0] = cpf que comprou assento 1)
        salvar_grafo(G)

# Função que carrega o grafo do arquivo
def carregar_grafo():
    # Abre arquivo e retorna os dados do grafo
    with open(ARQUIVO_GRAFO, 'r') as arq:
        dados_existentes = json.load(arq)
    
    # Cria novo grafo para armazenar dados do grafo retornado
    grafo = nx.DiGraph()

    # Salva cada trecho no grafo
    for trecho in dados_existentes['trecho']:
        grafo.add_edge(
            trecho['v1'], trecho['v2'], 
            distancia = trecho['distancia'], 
            assentos = trecho['assentos'],
            cpf = trecho['cpf'],
        )
    
    return grafo

# Função que carrega todas as passagens compradas no sistema
def carregar_passagens_compradas():
    try:
        with open(ARQUIVO_PASSAGENS_COMPRADAS, 'r') as arq:
            # Retorna dicionário (cpf são as chaves)
            return json.load(arq)
        
    except FileNotFoundError:
        # Retorna um dicionário vazio se o arquivo não existir (não teve nenhuma compra ainda)
        return {}

# Função que salva o grafo no arquivo (atualiza)
# Parâmetros ->     grafo_att: grafo dos trechos com informações atualizadas para ser salvo em arquivo
# Retorno ->        Sem retorno
def salvar_grafo(grafo_att):
    # Novo grafo a ser salvo em arquivo
    dados_novos = {'trecho': []}

    # Salva novos dados de cada trecho (atualiza na lista de cada trecho. LISTA = informações como distancia e etc)
    for v1, v2, atributos in grafo_att.edges(data=True):
        dados_novos['trecho'].append({
            'v1': v1,
            'v2': v2,
            'distancia': atributos['distancia'],
            'assentos': atributos['assentos'],
            'cpf': atributos['cpf'],
        })

    # Salva novo grafo em arquivo
    with open(ARQUIVO_GRAFO, 'w') as arq:
        json.dump(dados_novos, arq, indent=4)

# Função que salva um dicionário no arquivo (atualiza)
# Parâmetros ->     dicionario_att: dicionario das passagens com informações atualizadas para ser salvo em arquivo
# Retorno ->        Sem retorno
def salvar_passagem_comprada(dicionario_att):
    with open(ARQUIVO_PASSAGENS_COMPRADAS, 'w') as arq:
        json.dump(dicionario_att, arq, indent=4)

# Função que encontra 5 caminhos entre origem e destino, e retorna ordenado considerando distancia total (menor ao maior)
# Parâmetros ->     grafo: grafo dos trechos
#                   cidade_inicial: cidade origem para encontrar caminhos
#                   cidade_fim: cidade destino para encontrar caminhos
# Retorno ->        caminhos: lista de caminhos encontrados

# ps: Retorna uma lista de caminhos,  onde lista[0] = Servidor que ta retornando esses caminhos, lista[1 e etc] = caminhos
# ex:  [
#           "A",
#           ["curitiba", "bh", "rj", "sao paulo"],
#           ["curitiba", "cuiabá", "sao paulo"],
#           ... mais 3 pra fechar 5 (ou nao, se achar menos que 5)  
#      ]
def encontrar_caminhos(grafo, cidade_inicial, cidade_fim):
    caminhos = []
    
    # Retorna todos os caminhos possíveis entre origem e destino
    for path in nx.all_simple_paths(grafo, source=cidade_inicial, target=cidade_fim):

        # Verifica se algum trecho do caminho encontrado não possui assentos
        caminho_valido = True
        for i in range(len(path) - 1):
            trecho = (path[i], path[i + 1])
            if grafo[trecho[0]][trecho[1]]['assentos'] == 0:
                caminho_valido = False
                break
        
        if caminho_valido:
            # Calcula distancia do caminho encontrado
            dist = sum(grafo[path[i]][path[i + 1]]['distancia'] for i in range(len(path) - 1))

            # Organiza os caminhos em fila de prioridade (menor ao maior) a depender da distancia
            heapq.heappush(caminhos, (dist, path))

    # Se houver pelo menos um caminho válido, extrai os caminhos e insere "A" no início. Não precisa mais da distância
    if caminhos:
        caminhos_ordenados = ["A"]  # Esse "A" vai indicar que os caminhos são do servidor A
        caminhos_ordenados.extend([heapq.heappop(caminhos)[1] for _ in range(min(len(caminhos), 5))])
    
    # Caso não haja caminhos válidos, retorna uma lista vazia
    else:
        caminhos_ordenados = []
    
    return caminhos_ordenados

# Função para verificar se existe compras em um CPF
# Parâmetros ->     cpf: cpf de um cliente para verificar suas compras
# Retorno ->        compras: lista de compras encontradas para um CPF

# Se existir compras, retorna uma lista de dicionários, onde cada dicionário representa uma compra
# ex: [ 
#       "A",
#       {'trechos': [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ], 'assentos': [1, 3], 'distancia': 1234, 'valor': 1000},
#       {'trechos': [ ('berlim', 'sao paulo'), ('salvador', 'fsa'), ('serrinha', 'bomfim') ], 'assentos': [3, 2, 1], 'distancia': 1234, 'valor': 23954},      
#     ]
def verifica_compras_cpf(cpf):
    # Carrega todas as compras do sistema
    compras = carregar_passagens_compradas()

    if cpf in compras:
        print("Achei passagens")
        compras_cliente = compras[cpf]
        
        # Indica que é do server A
        compras_cliente.insert(0, "A")
        
        return compras_cliente
    
    else:
        print("Não achei passagens")
        return []

# Função para verificar se os trechos escolhidos pelo cliente ainda estão disponível (compara com o arquivo atual)
# Parâmetros ->     G: grafo dos trechos atualizado do sistema
#                   trechos: trechos escolhidos pelo cliente
# Retorno ->        comprar: flag que indica se o caminho ainda está disponível (True) ou não (False)

# Agora recebe essa estrutura: [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ]
def verifica_trechos_escolhidos(G, trechos):
    comprar = True

    for origem, destino in trechos:
        # Se algum trecho do caminho escolhido pelo cliente não tiver mais assento, caminho ta indisponível
        if G[origem][destino]['assentos'] == 0:
            comprar = False
            break
        
    return comprar

# Função para registrar compra de trechos (atualiza grafo, salva compra de passagem e atualiza os arquivos)
# Parâmetros ->     G: grafo com trechos do sistema
#                   caminho: trechos escolhidos pelo cliente
#                   cpf: cpf do cliente que está comprando o trecho
# Retorno ->        Sem retorno

# Agora recebe essa estrutura: [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ]
def registra_trechos_escolhidos(G, trechos, cpf):
    # Número do assento em cada trecho
    assentos = []
    
    for origem, destino in trechos:
        # Atualiza o número de assentos e associa o CPF ao trecho
        G[origem][destino]['assentos'] -= 1
        G[origem][destino]['cpf'].append(cpf)

        # Adiciona número de assento referente a posição do cpf na lista de cada trecho
        # Se um trecho tem 3 cpf's, o tamanho da sua lista é 3, logo o número do assento do ultimo cpf adicionado é 3
        assentos.append(len(G[origem][destino]['cpf']))
    
    salvar_grafo(G)

    # Atualiza dicionário com nova passagem comprada e salva em arquivo
    registra_compra(G, cpf, trechos, assentos)

# Função para registrar nova compra de passagem em um CPF (salva em arquivo)
# Parâmetros ->     cpf: cpf do cliente que está comprando uma passagem
#                   trechos: lista contendo tuplas onde cada tupla contém par de cidade (trecho)
#                   distancia: numero em km da distancia total do caminho (soma dos trechos)
#                   assentos: lista contendo numeração dos assentos em cada trecho que forma o caminho
# Retorno ->        Sem retorno

# ps: É um dicionário geral onde a chave vai ser o CPF e o valor de cada CPF vai ser uma lista
# A cada nova compra em um CPF, é adicionado um dicionário nessa lista, logo é uma lista de dicionários
# ex: {
#      "2347567" : [ 
#                    {'trechos': [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ], 'assentos': [1, 3], 'distancia': 1234, 'valor': 1000},
#                    {'trechos': [ ('berlim', 'sao paulo'), ('salvador', 'fsa'), ('serrinha', 'bomfim') ], 'assentos': [3, 2, 1], 'distancia': 1234, 'valor': 23954},      
#                  ],
#      "6754234" : lista com compras desse cpf .....          
#     }

# Agora recebe essa estrutura: [ ('cuiabá', 'sao paulo'), ('minas', 'salvador') ]
def registra_compra(G, cpf, trechos, assentos):
    valor_passagem = 0
    distancia_passagem = 0

    # Itera sobre os trechos para calcular valor pago e a distância total
    for origem, destino in trechos:
        dist = G[origem][destino]['distancia']

        valor_passagem += valor_trecho(dist)  # Função para calcular valor com base na distância
        distancia_passagem += dist

    # Carrega todas as compras do sistema
    compras =  carregar_passagens_compradas()

    # Cria uma nova compra
    compra_att = {"trechos": trechos, "assentos": assentos, "distancia": distancia_passagem, "valor": valor_passagem}
    
    # Se já existir uma compra no cpf, adiciona nova compra no cpf (mais um dicionário a lista)
    if cpf in compras:
        compras[cpf].append(compra_att)
    
    # Se não existir, cria uma nova chave no dicionário geral
    else:
        compras[cpf] = [compra_att]

    # Salva dicionário atualizado no arquivo
    salvar_passagem_comprada(compras)

# Recebe a escolha do caminho do cliente e separa a qual servidor pertence cada trecho
# Estrututa da tupla recebida: tupla[0] = lista contendo servidor a qual cada trecho pertence; tupla[1] = trechos (forma caminho)
# (
#   ["B", "A"], ["curitiba", "cuiabá", "sao paulo"]
# )

# Retorna 1 tupla contendo 3 listas: 1 contendo trechos do server A, 1 contenco trechos do server B e 
# 1 contendo trechos do server C
# ps: cada item das lista é uma tupla contendo um trecho

# ex: ( 
#       [ ('cuiabá', 'sao paulo'), aqui poderia ter outra tupla com um trecho por exemplo ], 
#       [ ('curitiba', 'cuiabá') ], 
#       []
#     )

# Dessa forma consigo reenviar os trechos aos seus devidos servidores
def desempacota_caminho_cliente(tupla):
    servidores = {"A": [], "B": [], "C": []}  # Dicionário para armazenar os trechos de cada servidor

    # Percorre a lista de servidores e associa os trechos correspondentes
    for i in range(len(tupla[0])):
        servidor = tupla[0][i]  # Obtém o servidor do trecho atual
        # Adiciona o par de cidades (trecho) ao servidor correspondente
        servidores[servidor].append( (tupla[1][i], tupla[1][i + 1]) )
        
    return servidores["A"], servidores["B"], servidores["C"]

# Verifica qual servidor encontrou caminho e adiciona numa lista
# ps: Printa qual servidor encontrou ou não
def servidor_encontrou_caminho(caminhos_a, caminhos_b, caminhos_c):
    caminhos_servidores = []
    
    for i, caminho in enumerate([caminhos_a, caminhos_b, caminhos_c]):
        if caminho:
            print(f"Servidor {nomes_servidores[i]} encontrou caminho.")
            caminhos_servidores.append(caminho)
        else:
            print(f"Servidor {nomes_servidores[i]} não encontrou caminho.")
    
    return caminhos_servidores

# Verifica qual servidor encontrou passagens e adiciona numa lista
# ps: Printa qual servidor encontrou ou não
def servidor_encontrou_passagem(passagens_a, passagens_b, passagens_c):
    passagens_servidores = []
    
    for i, caminho in enumerate([passagens_a, passagens_b, passagens_c]):
        if caminho:
            print(f"Servidor {nomes_servidores[i]} encontrou passagem.")
            passagens_servidores.append(caminho)
        else:
            print(f"Servidor {nomes_servidores[i]} não encontrou passagem.")
    
    return passagens_servidores