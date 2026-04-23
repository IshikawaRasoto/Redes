import socket

HOST = '127.0.0.1' 
# Porta maior que 1024, conforme exigido no trabalho 
PORT = 8080        

# AF_INET = IPv4 | SOCK_DGRAM = Protocolo UDP 
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Vincula o socket ao endereço e porta escolhidos
server_socket.bind((HOST, PORT))

print(f"[*] Servidor UDP escutando em {HOST}:{PORT}...")

while True:
    data, client_address = server_socket.recvfrom(1024)
    
    # Decodifica os bytes recebidos para string
    mensagem = data.decode('utf-8')
    print(f"[+] Mensagem recebida de {client_address}: {mensagem}")

    # Envia uma resposta de volta para o endereço do cliente
    resposta = "ACK: Hello recebido pelo Servidor!"
    server_socket.sendto(resposta.encode('utf-8'), client_address)