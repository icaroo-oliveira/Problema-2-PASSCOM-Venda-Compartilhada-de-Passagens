import requests

# Tempos random para verificação novamente de trechos disponíveis
times = (0.1, 0.15, 0.2, 0.25, 0.3)

# Requisições do tipo get
def requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout):
    try:
        response = requests.get(server_url+requisicao, json=mensagem, timeout=timeout)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Caminhos encontrados pelo server
        resposta = response.json()[chave_dicionario]
        
        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}")
        return None
    
# Requisições do tipo post
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
    
# Requisições do tipo delete (ROLLBACK)
def requests_delete(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout):
    try:
        response = requests.delete(server_url+requisicao, json=mensagem, timeout=timeout)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado da compra
        resposta = response.json()[chave_dicionario]

        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None

# Função para solicitar caminhos ou passagens de um servidor específico (thread)
def solicitar_caminhos_ou_passagens(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao, timeout):
    caminhos = requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout)
    if caminhos is not None:
        resultados[nome_servidor] = caminhos
    else:
        resultados[nome_servidor] = []

# Função para solicitar comprar de um servidor específico (thread)
def solicitar_comprar(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao, timeout):
    resposta, status = requests_post(server_url, requisicao, mensagem, chave_dicionario, nome_servidor, timeout)

    resultados[nome_servidor] = (resposta, status)
    
