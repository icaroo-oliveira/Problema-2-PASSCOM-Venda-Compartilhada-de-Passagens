import requests

# Requisições do tipo get
def requests_get(server_url, identificador, mensagem, chave_dicionario, nome_servidor):
    try:
        response = requests.get(server_url+identificador, json=mensagem, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Caminhos encontrados pelo server
        resposta = response.json()[chave_dicionario]
        
        return resposta
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}")
        return None
    
# Requisições do tipo post
def requests_post(server_url, identificador, mensagem, chave_dicionario, nome_servidor):
    try:
        response = requests.post(server_url+identificador, json=mensagem, timeout=10)
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx

        # Resultado da compra
        resposta = response.json()[chave_dicionario]

        return resposta    
    
    # Caso request de algum erro de conexão, timeout e etc
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ocorreu um erro no servidor {nome_servidor}: {e}") 
        return None
