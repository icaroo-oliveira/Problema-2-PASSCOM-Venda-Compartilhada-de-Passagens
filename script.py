import subprocess
import time
import threading

client_script = "client_script.py"
cont=111111111111111
cont2 = 1
cont3 = 2


def abrir_terminal(escolhas):
    escolha_str = ' '.join(escolhas)
    #comando = f'gnome-terminal -- bash -c "python3 {client_script} {escolha_str}; exec bash"'
    comando = f'start cmd /k python {client_script} {escolha_str}'

    print(f"Executando comando: {comando}")

    # Executa o comando no sistema
    subprocess.Popen(comando, shell=True)

# Número de clientes/terminais
num_clients = 100








# Abrindo múltiplos terminais com os mesmos parâmetros
for i in range(num_clients):
    
    # if i%2==0:
    #     escolhas = ['3','1', '5', '1','4',str(cont)]
    # else:
    #     escolhas = ['2','1', '10', '2','4',str(cont)]

    escolhas = ['1','1', '6', '2','4',str(cont)]
    abrir_terminal(escolhas)
    cont+=1
    
   