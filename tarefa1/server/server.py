# Aluno: Rafael Eijy Ishikawa Rasoto
# Trabalho 1 - Redes de Computadores UTFPR

import argparse
import socket
import os
import sys
import threading
import time

# Adiciona o diretório pai no path para importar protocolo.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import protocolo

def main():
    # --- FASE DE INICIALIZAÇÃO ---
    argparser = argparse.ArgumentParser(description="Servidor UDP para transferência de arquivos")
    argparser.add_argument('--port', type=int, required=True, help='Porta do servidor')
    args = argparser.parse_args()
    
    HOST = '127.0.0.1' 
    PORT = args.port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print(f"[*] Servidor UDP escutando em {HOST}:{PORT}...")

    # --- FASE DE REQUISIÇÃO (GET) ---
    while True:
        data, endereco_client = server_socket.recvfrom(1024)
        
        try:
            msg = protocolo.desempacotar_pacote(data)
        except ValueError:
            continue # Ignora pacotes malformados
            
        if not msg['integro'] or msg['tipo'] != b'G':
            continue # Ignora pacotes corrompidos ou inesperados

        nome_arquivo = msg['dados'].decode('utf-8').strip()
        print(f"[+] Nova requisição de {endereco_client}: '{nome_arquivo}'")
        
        if not nome_arquivo or "/" in nome_arquivo or "\\" in nome_arquivo:
            server_socket.sendto(protocolo.gerar_pacote(b'X', 0, b"400 Bad Request"), endereco_client)
        else:
            caminho_arquivo = os.path.join("files", nome_arquivo)
            
            if os.path.isfile(caminho_arquivo):
                threading.Thread(target=handle_client, args=(endereco_client[0], endereco_client[1], caminho_arquivo)).start()
            else:
                erro = f"404 Not Found: '{nome_arquivo}' nao existe."
                server_socket.sendto(protocolo.gerar_pacote(b'X', 0, erro.encode('utf-8')), endereco_client)


def handle_client(client_ip: str, client_port: int, filename: str):
    # --- FASE DE HANDSHAKE (BEGIN) ---
    thread_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        thread_socket.bind(('', 0))
        thread_socket.settimeout(5.0)

        # Envia pacote B (Begin) para sinalizar que o arquivo existe
        thread_socket.sendto(protocolo.gerar_pacote(b'B', 0), (client_ip, client_port))

        try:
            data, addr = thread_socket.recvfrom(1024)
            msg = protocolo.desempacotar_pacote(data)
            
            if addr == (client_ip, client_port) and msg['tipo'] == b'A' and msg['sequencia'] == 0:
                print(f"[Thread {client_port}] Handshake concluído. Iniciando envio.")
                transferir_arquivo(thread_socket, (client_ip, client_port), filename)
            else:
                print(f"[Thread {client_port}] Falha no Handshake: ACK esperado não recebido.")
        except socket.timeout:
            print(f"[Thread {client_port}] Timeout: Cliente não confirmou o Handshake.")

    except Exception as e:
        print(f"[Thread {client_port}] Erro na thread: {e}")
    finally:
        thread_socket.close()


def transferir_arquivo(thread_socket: socket.socket, endereco_cliente: tuple, caminho_arquivo: str, timeout_ms: int = 10, max_tentativas: int = 5):
    # --- FASE DE TRANSFERÊNCIA DE DADOS (STOP-AND-WAIT) ---
    TAMANHO_PACOTE = 512
    seq_num = 0
    pacotes_perdidos = set()
    inicio_transferencia = time.time()
    
    thread_socket.settimeout(timeout_ms / 1000.0)

    with open(caminho_arquivo, 'rb') as arquivo:
        while True:
            pedaco = arquivo.read(TAMANHO_PACOTE)
            if not pedaco:
                break
                
            mensagem_dados = protocolo.gerar_pacote(b'D', seq_num, pedaco)
            ack_confirmado = False
            tentativas = 0

            while not ack_confirmado and tentativas < max_tentativas:
                thread_socket.sendto(mensagem_dados, endereco_cliente)

                try:
                    data, addr = thread_socket.recvfrom(1024)
                    resposta = protocolo.desempacotar_pacote(data)

                    if resposta['tipo'] == b'A' and resposta['sequencia'] == seq_num:
                        ack_confirmado = True
                        seq_num += 1
                except socket.timeout:
                    tentativas += 1
                    pacotes_perdidos.add(seq_num)
                    print(f"    [!] Timeout Seq {seq_num}. Reenviando ({tentativas}/{max_tentativas})...")
                except ValueError:
                    continue # Ignora pacotes malformados

            if not ack_confirmado:
                print(f"[Thread {endereco_cliente[1]}] Conexão instável. Transferência abortada.")
                return 

    # --- FASE DE ENCERRAMENTO (EOF) ---
    thread_socket.sendto(protocolo.gerar_pacote(b'E', seq_num), endereco_cliente)

    fim_transferencia = time.time()
    tempo_total = fim_transferencia - inicio_transferencia
    velocidade = (os.path.getsize(caminho_arquivo) / 1024) / tempo_total if tempo_total > 0 else 0

    print(f"[Thread {endereco_cliente[1]}] Sucesso: '{os.path.basename(caminho_arquivo)}' enviado.")
    print(f"    - Tempo decorrido: {tempo_total:.2f} s")
    print(f"    - Velocidade: {velocidade:.2f} KB/s")
    print(f"    - Pacotes perdidos/retransmitidos: {len(pacotes_perdidos)}")

if __name__ == "__main__":
    main()
