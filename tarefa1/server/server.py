import argparse
import socket
import os
import struct
import hashlib
import threading

def main():
    HOST = '127.0.0.1' 
    # Porta maior que 1024, conforme exigido no trabalho 
    
    argparser = argparse.ArgumentParser(description="Servidor para transferência de arquivos usando UDP")
    argparser.add_argument('--port', type=int, help='Porta do servidor')
    args = argparser.parse_args()
    PORT = args.port


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

        # Tratamento da requisição:
        partes = mensagem.strip().split()

        if len(partes) != 2 or partes[0] != "GET":
            resposta = "400 Bad Request: formato esperado 'GET /{filename}.ext'"
        else:
            caminho_requisitado = partes[1]

            if not caminho_requisitado.startswith("/"):
                resposta = "400 Bad Request: caminho invalido"
            else:
                nome_arquivo = caminho_requisitado[1:]

                if not nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
                    resposta = "400 Bad Request: nome de arquivo invalido"
                else:
                    caminho_arquivo = os.path.join("files", nome_arquivo)

                    if os.path.isfile(caminho_arquivo):
                        print(f"Arquivo identificado, criando thread para cliente {client_address}...")
                        thread = threading.Thread(target=handle_client, args=(client_address[0], client_address[1], caminho_arquivo))
                        thread.start()
                    else:
                        resposta = f"404 Not Found: arquivo '{nome_arquivo}' nao existe"


def handle_client(client_ip: str, client_port: int, filename: str):
    thread_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    seq_num = 0

    thread_socket.bind(('', 0))  # Bind a uma porta aleatória disponível
    meu_ip, minha_porta = thread_socket.getsockname()
    print(f"[Thread] Iniciada para {client_ip}:{client_port} usando porta {minha_porta}")

    thread_socket.sendto(gerar_mensagem_comeco_transmissao(seq_num), (client_ip, client_port))
    seq_num += 1
    
    transfering = True
    while transfering:
        # Lógica de transferência de arquivos usando mensagens estruturadas
        pass


# Tipos de mensagem:
# 0 - Começando transmissão : 'B'
# 1 -> n-1 - Segmentos de dados : 'D'
# n - End of File : 'E'
# 
# Acknowledgement: 'A' 

# Estrutura da mensagem
# Cabecalho: 1 byte (tipo) + 4 bytes (numero de sequencia ou tamanho do nome do arquivo) + 16 bytes MD5 hash + data (variavel, dependendo do tipo)

def gerar_mensagem_ack(seq_num: int):
    return struct.pack('!cI', b'A', seq_num)

def gerar_mensagem_comeco_transmissao(seq_num: int):
    mensagem = struct.pack('!cI', b'B', seq_num)
    return mensagem


def gerar_mensagem_dados(seq_num, dados):
    return struct.pack('!cI', b'D', seq_num) + dados

def gerar_mensagem_eof(seq_num):
    return struct.pack('!cI', b'E', seq_num)

def calcular_checksum(dados):
    return hashlib.md5(dados).hexdigest()

if __name__ == "__main__":
    main()
