import argparse
import socket
import os
import sys
import threading
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import protocolo

class TCPClient:
    def __init__(self, on_chat=None, on_download_start=None, on_download_chunk=None, on_download_eof=None, on_error=None, on_conn_lost=None):
        self.sock = None
        self.connected = False
        self.download_state = {
            'in_progress': False,
            'file': None,
            'expected_sha256': '',
            'expected_size': 0,
            'received_size': 0,
            'filename': ''
        }
        self.on_chat = on_chat
        self.on_download_start = on_download_start
        self.on_download_chunk = on_download_chunk
        self.on_download_eof = on_download_eof
        self.on_error = on_error
        self.on_conn_lost = on_conn_lost
        self.thread_recepcao = None

    def connect(self, ip, port, timeout=5.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.connect((ip, port))
        self.sock.settimeout(None)
        self.connected = True
        self.thread_recepcao = threading.Thread(target=self._receptor_loop, daemon=True)
        self.thread_recepcao.start()

    def disconnect(self):
        if self.sock:
            try:
                protocolo.enviar_mensagem(self.sock, b'E')
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
        self.sock = None
        self.connected = False
        self.download_state['in_progress'] = False
        if self.download_state['file']:
            try:
                self.download_state['file'].close()
            except Exception:
                pass
            self.download_state['file'] = None

    def send_chat(self, msg):
        if self.connected and self.sock:
            protocolo.enviar_mensagem(self.sock, b'C', msg.encode('utf-8'))

    def request_file(self, filename):
        if self.connected and self.sock:
            protocolo.enviar_mensagem(self.sock, b'G', filename.encode('utf-8'))

    def _receptor_loop(self):
        try:
            while self.connected and self.sock:
                tipo, payload = protocolo.receber_mensagem(self.sock)
                
                if tipo == b'C':
                    mensagem = payload.decode('utf-8')
                    if self.on_chat:
                        self.on_chat(mensagem)
                        
                elif tipo == b'S':
                    partes = payload.decode('utf-8').split('|')
                    filename = partes[0]
                    tamanho = int(partes[1])
                    sha256 = partes[2]
                    
                    caminho = f"arquivo_recebido_{filename}"
                    self.download_state['file'] = open(caminho, 'wb')
                    self.download_state['expected_sha256'] = sha256
                    self.download_state['expected_size'] = tamanho
                    self.download_state['received_size'] = 0
                    self.download_state['filename'] = filename
                    self.download_state['in_progress'] = True
                    
                    if self.on_download_start:
                        self.on_download_start(filename, tamanho, sha256)
                        
                elif tipo == b'D':
                    if self.download_state['in_progress'] and self.download_state['file']:
                        self.download_state['file'].write(payload)
                        self.download_state['received_size'] += len(payload)
                        if self.on_download_chunk:
                            self.on_download_chunk(self.download_state['received_size'], self.download_state['expected_size'])
                            
                elif tipo == b'F':
                    if self.download_state['in_progress'] and self.download_state['file']:
                        self.download_state['file'].close()
                        self.download_state['file'] = None
                        self.download_state['in_progress'] = False
                        if self.on_download_eof:
                            self.on_download_eof(self.download_state['filename'], self.download_state['expected_sha256'])
                            
                elif tipo == b'X':
                    mensagem = payload.decode('utf-8')
                    self.download_state['in_progress'] = False
                    if self.download_state['file']:
                        try:
                            self.download_state['file'].close()
                        except Exception:
                            pass
                        self.download_state['file'] = None
                    if self.on_error:
                        self.on_error(mensagem)
                        
        except (ConnectionError, socket.error):
            self.connected = False
            if self.on_conn_lost:
                self.on_conn_lost()
        except Exception as e:
            self.connected = False
            if self.on_conn_lost:
                self.on_conn_lost()

def calcular_sha256_local(caminho):
    hasher = hashlib.sha256()
    with open(caminho, 'rb') as arquivo:
        while True:
            bloco = arquivo.read(8192)
            if not bloco:
                break
            hasher.update(bloco)
    return hasher.hexdigest()

def exibir_menu():
    print("\n--- Menu Interativo ---")
    print("1. Chat (Enviar mensagem)")
    print("2. Arquivo (Requisitar arquivo)")
    print("3. Sair")
    print("-----------------------")

def main():
    parser = argparse.ArgumentParser(description="Cliente TCP")
    parser.add_argument('--serverip', type=str, required=True, help='IP do servidor')
    parser.add_argument('--serverport', type=int, required=True, help='Porta do servidor')
    args = parser.parse_args()
    
    def cli_on_chat(msg):
        print(f"\n[Chat] {msg}\n> ", end="", flush=True)

    def cli_on_download_start(filename, size, sha):
        print(f"\n[Download] Iniciando download de '{filename}' ({size} bytes)...")

    def cli_on_download_chunk(received, total):
        porcentagem = (received / total) * 100 if total > 0 else 0
        print(f"\r[Download] Progresso: {porcentagem:.1f}% ({received}/{total} bytes)", end="", flush=True)

    def cli_on_download_eof(filename, expected_sha256):
        caminho = f"arquivo_recebido_{filename}"
        print(f"\n[Download] Concluido. Verificando hash...")
        sha_calculado = calcular_sha256_local(caminho)
        if sha_calculado == expected_sha256:
            print("[Download] HASH OK! Arquivo integro.")
            print(f"  - SHA-256: {sha_calculado}")
        else:
            print("[Download] ERRO DE HASH! Arquivo corrompido.")
            print(f"  - Esperado:  {expected_sha256}")
            print(f"  - Calculado: {sha_calculado}")
        print("> ", end="", flush=True)

    def cli_on_error(msg):
        print(f"\n[Erro do Servidor] {msg}\n> ", end="", flush=True)

    def cli_on_conn_lost():
        print("\n[-] Conexao com o servidor finalizada.")
        os._exit(0)

    client = TCPClient(
        on_chat=cli_on_chat,
        on_download_start=cli_on_download_start,
        on_download_chunk=cli_on_download_chunk,
        on_download_eof=cli_on_download_eof,
        on_error=cli_on_error,
        on_conn_lost=cli_on_conn_lost
    )
    
    try:
        client.connect(args.serverip, args.serverport)
    except Exception as e:
        print(f"[-] Nao foi possivel conectar ao servidor: {e}")
        sys.exit(1)
        
    print("[+] Conectado com sucesso ao servidor.")
    exibir_menu()
    
    try:
        while True:
            opcao = input("> ").strip()
            if not opcao:
                continue
                
            if opcao == '1':
                mensagem = input("Digite a mensagem de chat: ").strip()
                if mensagem:
                    try:
                        client.send_chat(mensagem)
                    except Exception as e:
                        print(f"[-] Erro ao enviar: {e}")
                        break
                        
            elif opcao == '2':
                if client.download_state['in_progress']:
                    print("Aguarde a finalizacao do download atual.")
                    continue
                nome_arquivo = input("Digite o nome do arquivo desejado: ").strip()
                if nome_arquivo:
                    try:
                        client.request_file(nome_arquivo)
                    except Exception as e:
                        print(f"[-] Erro ao enviar: {e}")
                        break
                        
            elif opcao == '3':
                client.disconnect()
                break
            else:
                print("Opcao invalida.")
                exibir_menu()
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()
        print("[*] Conexao encerrada.")

if __name__ == "__main__":
    main()
