import argparse
import socket
import os
import sys
import threading
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import protocolo

class ClienteConexao:
    def __init__(self, socket_cliente, endereco):
        self.socket = socket_cliente
        self.endereco = endereco
        self.lock = threading.Lock()

    def enviar(self, tipo, payload=b''):
        with self.lock:
            protocolo.enviar_mensagem(self.socket, tipo, payload)

clientes_ativos = set()
clientes_lock = threading.Lock()

def registrar_cliente(cliente):
    with clientes_lock:
        clientes_ativos.add(cliente)

def remover_cliente(cliente):
    with clientes_lock:
        if cliente in clientes_ativos:
            clientes_ativos.remove(cliente)

def broadcast_chat(mensagem, remetente=None):
    payload = mensagem.encode('utf-8')
    with clientes_lock:
        for cliente in list(clientes_ativos):
            if cliente != remetente:
                try:
                    cliente.enviar(b'C', payload)
                except Exception:
                    pass

def servidor_input_loop():
    while True:
        try:
            texto = input()
            if not texto.strip():
                continue
            broadcast_chat(f"Servidor: {texto}")
        except EOFError:
            break
        except Exception:
            pass

def calcular_sha256_arquivo(caminho):
    hasher = hashlib.sha256()
    with open(caminho, 'rb') as arquivo:
        while True:
            bloco = arquivo.read(8192)
            if not bloco:
                break
            hasher.update(bloco)
    return hasher.hexdigest()

def obter_caminho_seguro(pasta_raiz, caminho_requisitado):
    pasta_raiz = os.path.abspath(pasta_raiz)
    caminho_completo = os.path.abspath(os.path.join(pasta_raiz, caminho_requisitado))
    if os.path.commonpath([pasta_raiz, caminho_completo]) != pasta_raiz:
        raise PermissionError("Path Traversal detectado.")
    return caminho_completo

def enviar_arquivo(cliente, caminho_arquivo, nome_arquivo):
    try:
        tamanho = os.path.getsize(caminho_arquivo)
        sha256 = calcular_sha256_arquivo(caminho_arquivo)
        
        info_inicio = f"{nome_arquivo}|{tamanho}|{sha256}"
        cliente.enviar(b'S', info_inicio.encode('utf-8'))
        
        with open(caminho_arquivo, 'rb') as arquivo:
            while True:
                bloco = arquivo.read(8192)
                if not bloco:
                    break
                cliente.enviar(b'D', bloco)
                
        cliente.enviar(b'F')
        print(f"[Thread {cliente.endereco[1]}] Arquivo {nome_arquivo} enviado com sucesso.")
    except Exception as e:
        print(f"[Thread {cliente.endereco[1]}] Erro ao enviar arquivo: {e}")
        try:
            cliente.enviar(b'X', f"Erro de transferencia: {str(e)}".encode('utf-8'))
        except Exception:
            pass

def gerenciar_cliente(socket_cliente, endereco):
    print(f"[+] Conexao aceita de {endereco}")
    cliente = ClienteConexao(socket_cliente, endereco)
    registrar_cliente(cliente)
    
    try:
        while True:
            tipo, payload = protocolo.receber_mensagem(socket_cliente)
            
            if tipo == b'E':
                print(f"[-] Cliente {endereco} solicitou saida.")
                break
                
            elif tipo == b'C':
                mensagem = payload.decode('utf-8')
                print(f"[Chat] Cliente {endereco[1]}: {mensagem}")
                broadcast_chat(f"Cliente {endereco[1]}: {mensagem}", remetente=cliente)
                
            elif tipo == b'G':
                nome_arquivo = payload.decode('utf-8').strip()
                print(f"[Get] Cliente {endereco[1]} requisitou: {nome_arquivo}")
                
                try:
                    caminho_arquivo = obter_caminho_seguro("files", nome_arquivo)
                    if os.path.isfile(caminho_arquivo):
                        threading.Thread(target=enviar_arquivo, args=(cliente, caminho_arquivo, nome_arquivo)).start()
                    else:
                        erro = f"404 Not Found: {nome_arquivo} nao existe."
                        cliente.enviar(b'X', erro.encode('utf-8'))
                except PermissionError:
                    erro = "403 Forbidden: Acesso fora do diretorio permitido."
                    cliente.enviar(b'X', erro.encode('utf-8'))
                    print(f"[Seguranca] Tentativa de Path Traversal de {endereco} para '{nome_arquivo}'")
                    
    except (ConnectionError, socket.error):
        print(f"[-] Conexao com {endereco} perdida.")
    finally:
        remover_cliente(cliente)
        socket_cliente.close()

def main():
    parser = argparse.ArgumentParser(description="Servidor TCP Multithread")
    parser.add_argument('--port', type=int, required=True, help='Porta do servidor')
    args = parser.parse_args()
    
    HOST = '127.0.0.1'
    PORT = args.port
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"[*] Servidor TCP escutando em {HOST}:{PORT}...")
    
    input_thread = threading.Thread(target=servidor_input_loop)
    input_thread.daemon = True
    input_thread.start()
    
    try:
        while True:
            socket_cliente, endereco = server_socket.accept()
            thread_cliente = threading.Thread(target=gerenciar_cliente, args=(socket_cliente, endereco))
            thread_cliente.daemon = True
            thread_cliente.start()
    except KeyboardInterrupt:
        print("\n[*] Servidor encerrado.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
