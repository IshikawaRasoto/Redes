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
    """
    Thread responsável por gerenciar a transferência de um arquivo específico.
    """

    TAMANHO_CABECALHO = 21
    TAMANHO_PACOTE = 1024

    # AF_INET = IPv4 | SOCK_DGRAM = UDP
    thread_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        thread_socket.bind(('', 0))
        porta_escolhida = thread_socket.getsockname()
        print(f"[Thread] Atendimento iniciado para {client_ip} na porta {porta_escolhida}")

        # Configura um timeout para o handshake não travar a thread se o cliente sumir
        thread_socket.settimeout(5.0)

        msg_confirmacao = b"200_OK"
        thread_socket.sendto(msg_confirmacao, (client_ip, client_port))

        try:
            data, addr = thread_socket.recvfrom(1024)
            
            if addr == (client_ip, client_port) and data == b"ACK_START":
                print(f"[Thread] Handshake concluído com {client_ip}:{client_port}. Iniciando fatiamento.")
                
                # CHAMA A FUNÇÃO DE TRANSFERÊNCIA REAL AQUI
                # transferir_arquivo(thread_socket, (client_ip, client_port), filename)
                
            else:
                print(f"[Thread] Erro no handshake: Mensagem inválida de {addr}")

        except socket.timeout:
            print(f"[Thread] Timeout: O cliente {client_ip}:{client_port} não confirmou o início.")

    except Exception as e:
        print(f"[Thread] Erro crítico na thread: {e}")
    
    finally:
        # 5. Encerramento (Passo 9)
        thread_socket.close()
        print(f"[Thread] Socket na porta {porta_escolhida} encerrado.")

        # Tamanho fixo do cabeçalho baseado na sua estrutura
    

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
