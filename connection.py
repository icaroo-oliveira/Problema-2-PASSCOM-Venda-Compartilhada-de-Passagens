import requests

# Requisições do tipo get
def requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor):
    try:
        response = requests.get(server_url+requisicao, json=mensagem, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Caminhos encontrados pelo server
        resposta = response.json()[chave_dicionario]
        
        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}")
        return None
    
# Requisições do tipo post
def requests_post(server_url, requisicao, mensagem, chave_dicionario, nome_servidor):
    try:
        response = requests.post(server_url+requisicao, json=mensagem, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado da compra
        resposta = response.json()[chave_dicionario]

        return resposta, response.status_code 
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None, None
    
# Requisições do tipo delete (ROLLBACK)
def requests_delete(server_url, requisicao, mensagem, chave_dicionario, nome_servidor):
    try:
        response = requests.delete(server_url+requisicao, json=mensagem, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado da compra
        resposta = response.json()[chave_dicionario]

        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None

# Função para solicitar caminhos ou passagens de um servidor específico
def solicitar_caminhos_ou_passagens(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao):
    caminhos = requests_get(server_url, requisicao, mensagem, chave_dicionario, nome_servidor)
    if caminhos is not None:
        resultados[nome_servidor] = caminhos
    else:
        resultados[nome_servidor] = []

# Função para solicitar comprar de um servidor específico
def solicitar_comprar(server_url, mensagem, chave_dicionario, nome_servidor, resultados, requisicao):
    resposta, status = requests_post(server_url, requisicao, mensagem, chave_dicionario, nome_servidor)

    resultados[nome_servidor] = (resposta, status)
    