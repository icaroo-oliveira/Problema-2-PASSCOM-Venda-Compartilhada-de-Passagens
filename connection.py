import requests

# Url de cada servidor
#SERVER_URL_A = "http://127.0.0.1:65433"
#SERVER_URL_B = "http://127.0.0.1:65434"
#SERVER_URL_C = "http://127.0.0.1:65435"

SERVER_URL_A = "http://server_a:65433"
SERVER_URL_B = "http://server_b:65434"
SERVER_URL_C = "http://server_c:65435"

#ou http://localhost:65433

# Tempos random para verificação novamente de trechos disponíveis (milésimos)
times = (0.1, 0.15, 0.2, 0.25, 0.3)

# Função para requisições do tipo get
# Parâmetros ->     server_url: url do servidor a fazer a requsição
#                   requisicao: indica qual operação servidor deve fazer (endpoint)
#                   mensagem: dados a enviar ao servidor
#                   chave_dicionario: identifica resposta do servidor
#                   nome_servidor: nome do servidor para exibir numa possível mensagem de erro
#                   timeout: tempo do timeout
# Retorno ->        resposta do servidor caso seja bem sucedido ou None caso ocorra algum erro
def requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout):
    try:
        response = requests.get(server_url+requisicao, json=mensagem, timeout=timeout)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        resposta = response.json()[chave_dicionario]
        
        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}")
        return None
    
# Função para requisições do tipo post
# Parâmetros ->     server_url: url do servidor a fazer a requsição
#                   requisicao: indica qual operação servidor deve fazer (endpoint)
#                   mensagem: dados a enviar ao servidor
#                   chave_dicionario: identifica resposta do servidor
#                   nome_servidor: nome do servidor para exibir numa possível mensagem de erro
#                   timeout: tempo do timeout
# Retorno ->        resposta do servidor + codigo status caso seja bem sucedido ou None caso ocorra algum erro
def requests_post(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout):
    try:
        response = requests.post(server_url+requisicao, json=mensagem, timeout=timeout)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado da compra
        resposta = response.json()[chave_dicionario]

        return resposta, response.status_code 
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None, None
    
# Função para requisições do tipo delete (ROLLBACK)
# Parâmetros ->     server_url: url do servidor a fazer a requsição
#                   requisicao: indica qual operação servidor deve fazer (endpoint)
#                   mensagem: dados a enviar ao servidor
#                   chave_dicionario: identifica resposta do servidor
#                   nome_servidor: nome do servidor para exibir numa possível mensagem de erro
#                   timeout: tempo do timeout
# Retorno ->        resposta do servidor caso seja bem sucedido ou None caso ocorra algum erro
def requests_delete(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout):
    try:
        response = requests.delete(server_url+requisicao, json=mensagem, timeout=timeout)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado do rollback
        resposta = response.json()[chave_dicionario]

        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None

# Função para solicitar caminhos ou passagens de um servidor específico (thread) e guardar em um dicionario
# Parâmetros ->     server_url: url do servidor a fazer a requsição
#                   mensagem: dados a enviar ao servidor
#                   chave_dicionario: identifica resposta do servidor
#                   nome_servidor: nome do servidor para exibir numa possível mensagem de erro
#                   resultados: dicionario para guardar respostas dos servidores
#                   requisicao: indica qual operação servidor deve fazer (endpoint)
#                   timeout: tempo do timeout
# Retorno ->        Sem retorno
def solicitar_caminhos_ou_passagens(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao, timeout):
    caminhos = requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout)
    
    if caminhos is not None:
        resultados[nome_servidor] = caminhos
    else:
        resultados[nome_servidor] = []

# Função para solicitar comprar de um servidor específico (thread) e guardar em um dicionario
# Parâmetros ->     server_url: url do servidor a fazer a requsição
#                   mensagem: dados a enviar ao servidor
#                   chave_dicionario: identifica resposta do servidor
#                   nome_servidor: nome do servidor para exibir numa possível mensagem de erro
#                   resultados: dicionario para guardar respostas e codigo de status dos servidores
#                   requisicao: indica qual operação servidor deve fazer (endpoint)
#                   timeout: tempo do timeout
# Retorno ->        Sem retorno
def solicitar_comprar(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao, timeout):
    resposta, status = requests_post(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout)

    resultados[nome_servidor] = (resposta, status)
    