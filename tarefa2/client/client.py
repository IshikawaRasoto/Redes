import argparse
import socket
import os
import sys
import threading
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import protocolo

download_state = {
    'in_progress': False,
    'file': None,
    'expected_sha256': '',
    'expected_size': 0,
    'received_size': 0,
    'filename': ''
}

def calcular_sha256_local(caminho):
    hasher = hashlib.sha256()
    with open(caminho, 'rb') as arquivo:
        while True:
            bloco = arquivo.read(8192)
            if not bloco:
                break
            hasher.update(bloco)
    return hasher.hexdigest()

def receptor_loop(sock):
    global download_state
    try:
        while True:
            tipo, payload = protocolo.receber_mensagem(sock)
            
            if tipo == b'C':
                mensagem = payload.decode('utf-8')
                print(f"\n[Chat] {mensagem}\n> ", end="", flush=True)
                
            elif tipo == b'S':
                partes = payload.decode('utf-8').split('|')
                filename = partes[0]
                tamanho = int(partes[1])
                sha256 = partes[2]
                
                caminho = f"arquivo_recebido_{filename}"
                download_state['file'] = open(caminho, 'wb')
                download_state['expected_sha256'] = sha256
                download_state['expected_size'] = tamanho
                download_state['received_size'] = 0
                download_state['filename'] = filename
                download_state['in_progress'] = True
                
                print(f"\n[Download] Iniciando download de '{filename}' ({tamanho} bytes)...")
                
            elif tipo == b'D':
                if download_state['in_progress'] and download_state['file']:
                    download_state['file'].write(payload)
                    download_state['received_size'] += len(payload)
                    porcentagem = (download_state['received_size'] / download_state['expected_size']) * 100
                    print(f"\r[Download] Progresso: {porcentagem:.1f}% ({download_state['received_size']}/{download_state['expected_size']} bytes)", end="", flush=True)
                    
            elif tipo == b'F':
                if download_state['in_progress'] and download_state['file']:
                    download_state['file'].close()
                    download_state['file'] = None
                    
                    caminho = f"arquivo_recebido_{download_state['filename']}"
                    print(f"\n[Download] Concluido. Verificando hash...")
                    
                    sha_calculado = calcular_sha256_local(caminho)
                    if sha_calculado == download_state['expected_sha256']:
                        print("[Download] HASH OK! Arquivo integro.")
                        print(f"  - SHA-256: {sha_calculado}")
                    else:
                        print("[Download] ERRO DE HASH! Arquivo corrompido.")
                        print(f"  - Esperado:  {download_state['expected_sha256']}")
                        print(f"  - Calculado: {sha_calculado}")
                    
                    download_state['in_progress'] = False
                    print("> ", end="", flush=True)
                    
            elif tipo == b'X':
                mensagem = payload.decode('utf-8')
                print(f"\n[Erro do Servidor] {mensagem}\n> ", end="", flush=True)
                download_state['in_progress'] = False
                
    except (ConnectionError, socket.error):
        print("\n[-] Conexao com o servidor finalizada.")
        os._exit(0)
    except Exception as e:
        print(f"\n[-] Erro na thread de recepcao: {e}")
        os._exit(1)

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
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((args.serverip, args.serverport))
    except Exception as e:
        print(f"[-] Nao foi possivel conectar ao servidor: {e}")
        sys.exit(1)
        
    print("[+] Conectado com sucesso ao servidor.")
    
    thread_recepcao = threading.Thread(target=receptor_loop, args=(sock,))
    thread_recepcao.daemon = True
    thread_recepcao.start()
    
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
                        protocolo.enviar_mensagem(sock, b'C', mensagem.encode('utf-8'))
                    except Exception as e:
                        print(f"[-] Erro ao enviar: {e}")
                        break
                        
            elif opcao == '2':
                if download_state['in_progress']:
                    print("Aguarde a finalizacao do download atual.")
                    continue
                nome_arquivo = input("Digite o nome do arquivo desejado: ").strip()
                if nome_arquivo:
                    try:
                        protocolo.enviar_mensagem(sock, b'G', nome_arquivo.encode('utf-8'))
                    except Exception as e:
                        print(f"[-] Erro ao enviar: {e}")
                        break
                        
            elif opcao == '3':
                try:
                    protocolo.enviar_mensagem(sock, b'E')
                except Exception:
                    pass
                break
            else:
                print("Opcao invalida.")
                exibir_menu()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()
        print("[*] Conexao encerrada.")

if __name__ == "__main__":
    main()
