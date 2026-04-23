import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

# AF_INET = IPv4 | SOCK_DGRAM = Protocolo UDP 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mensagem = "Hello do Cliente!"
print(f"[*] Enviando para {SERVER_HOST}:{SERVER_PORT} -> '{mensagem}'")

client_socket.sendto(mensagem.encode('utf-8'), (SERVER_HOST, SERVER_PORT))

# Aguarda a resposta do servidor
data, server_address = client_socket.recvfrom(1024)
print(f"[+] Resposta do servidor {server_address}: {data.decode('utf-8')}")

# Fecha o socket no cliente
client_socket.close()