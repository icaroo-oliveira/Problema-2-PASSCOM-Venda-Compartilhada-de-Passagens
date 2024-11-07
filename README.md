<h1 align="center"> PASSCOM: Venda de Compartilhada de Passagens</h1>

## Introdução
<div align="justify"> 

Expandindo a VendePASS, foi proposto um sistema onde três servidores seriam responsáveis pela venda de passagens, podendo um solicitar ao outro um determinado recurso, se houvesse necessidade. Para isso, entretanto, faz-se necessário uma colaboração e harmonização entre os servidores para que estes possam conseguir responder aos clientes.

O projeto, em sua completude, foi feito usando a linguagem de programação Python, que oferecia recursos diversos, como Mutexes, Threads e Eventos, que foram de vital importância para o desenvolvimento da solução, principalmente em questões de coerência e sincronização. Além disso, a mesma biblioteca de grafos (do Problema 1) foi utilizada para organização de rotas, por distância e disponibilidade.

Como resultado, criou-se uma estrutura que relaciona Cliente-Servidor e Servidor-Servidor, de modo que um servidor pode solicitar recursos de outros e ainda assim aceitar diversos clientes simultaneamente, de forma que um cliente não interfira com a compra do outro (estando ele conectado ao mesmo servidor ou não). Assim como no VendePASS, existe estabilidade em relação à conexão, no sentido de que ela ocorre em um período pequeno - somente no intervalo de envio e recebimento de dados - já ocorrendo a desconexão. O sistema é stateless (OSSAMA, 2023), por não guardar informações relevantes entre requisições e faz uso de uma API que foi construída utilizando o framework Flask.

## Metodologia e Resultados

**Arquitetura**: 

O sistema apresenta uma estrutura onde um servidor dispõe de um conjunto de métodos para troca de informações com os clientes e entre servidores. Para a implementação, foi usado o Protocolo de Transferência de Hipertexto(Hypertext Transfer Protocol), utilizando o micro-framework Flask para criação da API com métodos como GET e POST e seus respectivos endpoints. O uso do HTTP se deu pelo fato de ser um padrão flexível, sem estado e bem estruturado, que se localiza em cima do TCP, responsável pela entrega dos pacotes de dados (IBM,2024). Cada um dos três servidores é apoiado por dois arquivos no formato JSON. O primeiro para armazenamento de informações de passagens (que registrará informações das compras de uma pessoa/cpf como distância, número do assento, trajeto e valor) e o segundo, será um arquivo que conterá em si os trechos entre cidades, a distância entre essas cidades e os assentos disponíveis para cada trecho, além de também salvar informações do comprador de um assento de determinado trecho, como o CPF. 

Os módulos do cliente são apoiados por sub-módulos:
* O primeiro está relacionado a utilidades.
* O segundo é chamado *interface*. Que é um sub-módulo responsável por toda interatividade por parte do cliente. É um “módulo meio” responsável por coletar ‘’inputs’’ e passar para a parte de processamento.
* O último, comum também ao servidor, é o *connection*. Ele é o responsável por implementar as requisições como POST e GET.

Já o módulo do servidor é apoiado por dois sub-módulos:
* O primeiro é relacionado a utilidades do servidor, como a criação do grafo de trechos (já predefinido), carregar o grafo (trechos de viagem), carregar as passagens já compradas, salvar grafos e passagens, encontrar caminhos e verificações de compras em um CPF ou caminhos válidos. 
* O segundo é o *connection*, explicado acima, detêm as chamadas para POST, GET e algumas solicitações tipo de compras.

A arquitetura é caracterizado como de Microserviços com a possibilidade de compartilhamento de dados, visto que os servidores são independentes e podem cooperar ou não - cada um detém seus próprios arquivos JSON, cooperação essa que se da via API Restful. Além disso, se caracteriza também como arquitetura uma arquitetura distribuída.

**Protocolo de comunicação**: 

O protocolo de comunicação é via HTTP como já mencionado e feito com Flask. Foi criado métodos para POST e GET. 

Para comunicações que seguem a direção Cliente -> Servidor, os seguintes métodos são usados:

| **Endpoint**           | **Método HTTP** | **Descrição**                                                                                     |
|------------------------|-----------------|---------------------------------------------------------------------------------------------------|
| `/caminhos_cliente`    | GET             | Retorna os caminhos disponíveis de origem a destino, solicitado diretamente pelo cliente.|
| `/passagens_cliente`   | GET             | Verifica e retorna as passagens compradas pelo cliente, solicitado pelo próprio cliente. |
| `/comprar_cliente`     | POST            | Registra e verifica a compra de trechos, solicitado diretamente pelo cliente.            |

Todas essas requisições possuem o campo "mensagem", que pode assumir os seguintes valores:

| Mensagem (Cliente)                        | Significado                                                 |
|-------------------------------------------|------------------------------------------------------------ |
| "[Origem], [Destino]”                     | Solicitando caminhos entre [Origem] e [Destino].            |
| ”[Cpf],[Caminho]”                         | Comprando uma passagem para o [Caminho].                    |
| “[Cpf]”                                   | Solicitando passagens compradas por [Cpf].                  |


De outro modo, Servidor → Servidor (servidor enviando mensagem para servidor):

Existem métodos GET com os endpoints "/passagens_servidor" e "/caminhos_servidor", que são usados para a comunicação entre servidores, quando um servidor solicita um determinado recurso a outro. Por exemplo, um cliente pode se conectar ao servidor A, e o servidor A, por sua vez, conecta-se aos outros para retornar todas as passagens daquele usuário. O /caminhos_servidor, por outro lado, é utilizado quando um servidor solicita caminhos a outro servidor. Por fim, existe um método POST com o endpoint /comprar_servidor, que é usado quando um servidor solicita a outro a compra de trechos para que o caminho seja comprado pelo cliente mesmo se um trecho específico não tiver vaga no servidor conectado diretamente ao cliente.

| **Endpoint**           | **Método HTTP** | **Descrição**                                                                                      |
|------------------------|-----------------|----------------------------------------------------------------------------------------------------|
| `/caminhos_servidor`   | GET             | Retorna os caminhos disponíveis de origem a destino, conforme solicitado por outro servidor.       |
| `/passagens_servidor`  | GET             | Verifica e retorna as passagens compradas de um cliente, conforme solicitado por outro servidor.   |
| `/comprar_servidor`    | POST            | Registra e verifica a compra de trechos solicitada por outro servidor                              |

Também possuem um campo mensagem e possui semelhança com as mensagens das requições cliente-servidor.

Para além dos GET e POST, ainda no protocólo de comunicação, existem mensagens de ''rollback'' ou seja, mensagens que buscam desfazer algum tipo de alteração que tinha sido feita anteriormente. É usada pela lógica das compras sempre começarem do servidor onde foi conectado e dispara Threads para os outros servidores se eles tiverem trechos a cederem. Se o cliente conectou no servidor A e tem trechos envolvendo esse servidor a compra já é feita. Se tiver trechos de outros servidores, por exemplo do B, e está disponível, é feita a compra, mas se tiver um trecho no servidor C, e este não estiver disponível, é feito o rollback tanto em A quanto em B.

| Endpoint                   | Significado                                                                                                                                                                               |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/rollbaack        `       | Ordem de rollback (desfaz compra caso outro servidor não consiga realizar sua compra)                                                                                     |



**Roteamento**: 

Como é requerido o compartilhamento de trechos entre os servidores, a ideia do VendePASS precisou ser aprimorada para considerar a possibilidade de diferentes servidores oferecer seus trechos para completar um caminho, caso o servidor que o cliente conectou-se não tivesse tal trecho disponível. É importante salientar que os três servidores oferecem os mesmos trechos, com as mesmas cidades e com as mesmas distâncias. A diferença entre eles é o valor cobrado por 100km.

Depois de escolher a cidade origem e a cidade destino, o servidor conectado irá procurar pelo seus 10 melhores caminhos, ou seja, os caminhos mais curtos e com trechos com assentos disponíveis. A diferença agora, é que o servidor conectado também vai pedir aos outros dois servidores, os seus 10 melhores caminhos. No cenário perfeito, o servidor conectado vai retornar ao cliente 30 caminhos.

Essa somatória de caminhos, não é automaticamente exibida ao cliente. Primeiramente, os trechos desses caminhos, com marcações indicando a qual servidor pertence cada trecho, são misturados, tendo a possibilidade agora de formar novos caminhos com trechos de diferentes servidores. Por exemplo: o melhor caminho (mais curto e com assento) possível entre Salvador e Rio de Janeiro, não consegue ser formado no servidor A devido a falta de assento de um trecho desse caminho em questão; porém no servidor B, esse trecho está disponível em outro caminho e foi retornado. Ao procurar novamente os melhores caminhos, esse trecho do servidor B irá completar o melhor caminho possível que não podia ser formado no servidor A e esse caminho será disponibilizado ao cliente.

![Salvador-Rio de Janeiro](/imagens/meu_gif.gif)

Com a junção e mistura desses trechos, é necessário novamente separar os melhores caminhos, considerando agora duas métricas: os 5 caminhos mais curtos e os 5 caminhos mais baratos. Por decisão da equipe, caso um determinado trecho tenha sido retornado por mais de um servidor, é preciso escolher, ou seja, dar preferência a um servidor. Dessa forma, nos 5 caminhos mais baratos, caso tenha trechos retornados por diferentes servidores, irá usar o critério de servidor mais barato para determinar qual trecho será incorporado ao caminho e exibido ao cliente. Diferentemente, nos 5 caminhos mais curtos, irá usar o critério de dar preferência ao servidor conectado pelo cliente, visto que se um cliente conectou em um servidor n, ele quer a prioridade de comprar um trecho desse servidor. Caso o servidor conectado não tenha disponibilidade de tal trecho, o critério será o mesmo dos 5 caminhos mais baratos, visto que a distância de um trecho é igual em todos os servidores.

Seguindo essa lógica, um caminho pode ser encontrado misturando trechos dos três servidores, a depender da preferência. Assim, é possível encontrar de fato a melhor opção de compra para um cliente, utilizando e entrelaçando dados distribuídos entre os três servidores.

**Concorrência Distribuída**: 

Para lidar com a concorrência foi feito uso de um algorítmo que usava de Locks (responsáveis por travarem regiões críticas) e Threads para processarem compras de outros servidores. O Lock de um servidor é comum a todas requisições e endpoints. De modo que, uma operação de compra iniciada por um cliente e uma por outro servidor, compartilham do mesmo lock. Esse algoritmo preza sempre pelo cenário ideal, recebe o nome de "One Phase Commit", pois se existe uma necessidade de trecho de um servidor, ele já inicia a compra, mesmo que aquele server, nesse meio tempo possa ter perdido aquela vaga de alguma forma. Se esse cenário ocorrer, como já foi dito, é disparada uma ordem de "rollback".

<p align="center">
  <img src="/imagens/diagrama_sequencia_caso.png" width = "600" />
</p>
<p align="center"><strong> Figura 1. Fluxo de mensagens para uma compra bem sucedida envolvendo A e B </strong></p>
</strong></p>

Para os casos onde, por exemplo, uma ordem de rollback foi emitida para o servidor B, e esse cai antes de desfazer a alteração solicitada, o servidor que emitiu a ordem de rollback salva em um arquivo essa ordem, para posteriormente manda-lá novamente. A verificação de pendência de rollback é sempre emitida quando uma requisição - não importa se Get ou Post - ocorre, se a verificação acusar um ''rollback'' não realizado, a alteração é desfeita.

O diagrama de sequência abaixo, ilustra outros casos, como a compra ideal e trechos indisponíveis em outros servidores ou no próprio A.

<p align="center">
  <img src="/imagens/diagrama_sequencia.png" width = "600" />
</p>
<p align="center"><strong> Figura 2. Fluxo de mensagens para uma compra bem sucedida e não sucedida por falta de trechos </strong></p>
</strong></p>


**Confiabilidade da solução**: 

Se um cliente está fazendo uma compra no Servidor A e esse caí, é possível prosseguir com a compra a partir daquele momento. Isso se da pelo uso do paradigma Stateless provido pelo próprio HTTP.
Se um cliente está fazendo uma compra no Servidor A e esse compra trechos em outros servidores, e um desses não responde ou não tem mais trechos, a compra em A sofre Rollback.
A Priori, com a queda de servidores a consistência da concorrência distribuída se mantém, e mesmo que o servidor que o cliente se conectou (coordenador) tenha algum erro de conexão na requisição de compra, se manterá a persistência das ordens de rollbacks que devem ser realizadas por outros servidores.

**Avaliação da solução**: 
Foi criado um script para testes. 
* O primeiro cenário foi envolvendo somente um servidor A, de modo que 5 clientes tentam competir por 3 vagas, ocorreu tudo bem de modo que 2 clientes ficaram sem vagas, mas não foi computado nenhuma vaga que não existia.
* Já o segundo cenário envolvia agora três servidores A, B e C. O script se conectava ao Servidor B, e abria 5 terminais. O que ocorre é que para o Servidor A tinha 4 vagas para o trecho, e o B e C tinha 5 vagas para os respectivos trechos. A compra foi efetuada corretamente, e somente 4 passagens foram compradas, de modo que foi feito o rollback de uma delas.
* O Último script para testes envolveu uma magnitude muito grande de solicitações (100), onde no inicio das 100 solicitações ocorreu uma demora, mas conforme chegou na faixa dos 60-70 solicitações o fluxo aumentou rapidamente.
* O último, o script abria 20 terminais, sendo que os pares o cliente era conectado ao A e os impares o cliente era conectado ao B. O mesmo recursos eram solicitados, pelos testes o programa se comportou bem, apesar do número baixo de vagas (eram somente 10 para 20 clientes), assim como no primeiro caso, não houve incoerência relacionado ao número de vagas, seja por sobrecompra ou subcompra. Mais testes nesse cenário são necessários, para saber o quão balanceados estão sendo as compras feita em cada servidores e se será necessário algum sistema de Load balancing.

**Documentação do código**:
O código está completamente comentado e documentado.

**Emprego do Docker**:
Implementado. Foi criado Dockers para os servidor A, B e C e um para o cliente. Foi criado também um docker-compose, para orquestras o relacionamento das 4 entidades e o estabelecimento de uma rede entra elas no ambiente de testagem Docker.

**Conclusão**
Por fim, está sendo possível criar um sistema servidor-cliente e servidor-servidor robusto e resistente a falhas (com exceção da falha do nó principal), com forma maleável e eficaz. O fato de não haver registro de estados por parte do servidor, bem como as conexão só ocorrerem no momento de envio da mensagem, faz desse sistema bastante seguro. O servidor aceita múltiplas linhas de execução (Threads) e possui segurança no que diz respeito a acesso e segurança dos dados, evitando problemas como compras de uma passagem não mais disponível. De melhoras para o sistema, um sistema de cache para maior velocidade de processamento seria uma adição bem-vinda para o sistema, de forma adicionar ainda mais eficácia do servidor no processamento de requisições, além de um sistemas de "Lock" por trechos ou caminhos em vez de arquivos. Ademais, a adição de uma lógica que permitisse a não dependência do servidor coordenador em uma compra, permitiria maior confiabilidade. Por fim, um sistema de "Load balancing" seria interessante no tocante a distribuição de clientes por servidores. No mais foi possível criar contêiner para o servidor e cliente, proporcionando um ambiente de testagem seguro.


