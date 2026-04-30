# Aluno: Rafael Eijy Ishikawa Rasoto
# Trabalho 1 - Redes de Computadores UTFPR

import argparse
import socket
import os
import sys

# Adiciona o diretório pai no path para importar protocolo.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import protocolo

def main():
    # --- FASE DE INICIALIZAÇÃO ---
    parser = argparse.ArgumentParser(description="Client UDP para transferência de arquivos")
    parser.add_argument('--serverip', type=str, required=True, help='IP do servidor')
    parser.add_argument('--serverport', type=int, required=True, help='Porta do servidor')
    parser.add_argument('--filename', type=str, required=True, help='Nome do arquivo requisitado')
    parser.add_argument('--simulate_loss', action='store_true', help='Ativa a simulação de perda de pacotes')
    args = parser.parse_args()

    simular_perda = False
    arquivo_perda = "sim.txt"
    if args.simulate_loss:
        if not os.path.isfile(arquivo_perda):
            print(f"[-] Erro: Arquivo de configuração '{arquivo_perda}' ausente.")
            sys.exit(1)
        simular_perda = True
        print("[!] Simulação de perda de pacotes ativada.")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(5.0)

    # --- FASE DE HANDSHAKE ---
    print(f"[*] Solicitando arquivo '{args.filename}' para {args.serverip}:{args.serverport}...")
    pacote_get = protocolo.gerar_pacote(b'G', 0, args.filename.encode('utf-8'))
    client_socket.sendto(pacote_get, (args.serverip, args.serverport))

    try:
        data, endereco_servidor = client_socket.recvfrom(1024)
        msg_resposta = protocolo.desempacotar_pacote(data)
        
        if not msg_resposta['integro']:
            print("[-] Resposta inicial corrompida. Abortando.")
            sys.exit(1)

        if msg_resposta['tipo'] == b'B':
            print("[+] Requisição aceita. Iniciando transferência.")
            pacote_ack = protocolo.gerar_pacote(b'A', 0)
            client_socket.sendto(pacote_ack, endereco_servidor)
            
            # Remove o timeout do handshake e avança para a recepção
            client_socket.settimeout(None)
            receber_arquivo(client_socket, endereco_servidor, args.filename, simular_perda, arquivo_perda)
        elif msg_resposta['tipo'] == b'X':
            print(f"[-] Erro do servidor: {msg_resposta['dados'].decode('utf-8')}")
        else:
            print("[-] Resposta inesperada do servidor.")

    except socket.timeout:
        print("[-] Timeout aguardando resposta do servidor no handshake.")
    except Exception as e:
        print(f"[-] Erro de comunicação: {e}")
    finally:
        client_socket.close()


def receber_arquivo(client_socket: socket.socket, endereco_servidor: tuple, filename: str, simular_perda: bool, arquivo_perda: str):
    # --- FASE DE RECEPÇÃO DE DADOS ---
    fatias_recebidas = {}
    contagem_ignorados = 0
    client_socket.settimeout(5.0)
    
    try:
        while True:
            pacote_recebido, endereco = client_socket.recvfrom(1024)
            
            try:
                msg = protocolo.desempacotar_pacote(pacote_recebido)
            except ValueError:
                continue # Ignora pacotes malformados

            if msg['tipo'] == b'D':
                if not msg['integro']:
                    continue # Ignora pacotes corrompidos

                seq = msg['sequencia']
                
                # Trata pacote inédito
                if seq not in fatias_recebidas:
                    if simular_perda:
                        with open(arquivo_perda, 'r') as f:
                            linhas = f.readlines()
                            if contagem_ignorados < 3 and f"{seq}\n" in linhas:
                                print(f"[!] Simulando perda: ignorando pacote Seq {seq}")
                                contagem_ignorados += 1
                                continue
                                
                    fatias_recebidas[seq] = msg['dados']
                    contagem_ignorados = 0
                    
                # Envia ACK (mesmo para repetidos)
                client_socket.sendto(protocolo.gerar_pacote(b'A', seq), endereco)
            
            elif msg['tipo'] == b'E':
                print("[+] Pacote EOF recebido. Fim da recepção.")
                client_socket.sendto(protocolo.gerar_pacote(b'A', msg['sequencia']), endereco)
                break
                
    except socket.timeout:
        print("\n[-] Timeout na transferência. Abortando execução.")
        sys.exit(1)

    if not fatias_recebidas:
        print("[-] Nenhum dado recebido.")
        return

    # --- FASE DE RECONSTRUÇÃO ---
    print(f"[*] Reconstruindo arquivo ({len(fatias_recebidas)} pacotes)...")
    caminho_salvamento = os.path.join(os.getcwd(), f"arquivo_recebido_{filename}")
    
    with open(caminho_salvamento, 'wb') as arquivo_final:
        para_escrever = sorted(fatias_recebidas.keys())
        
        if len(para_escrever) - 1 != para_escrever[-1]:
            print("[-] ALERTA: Arquivo corrompido ou incompleto (pacotes perdidos).")
        
        for seq in para_escrever:
            arquivo_final.write(fatias_recebidas[seq])
            
    print(f"[+] Arquivo salvo com sucesso: {caminho_salvamento}")

if __name__ == "__main__":
    main()
