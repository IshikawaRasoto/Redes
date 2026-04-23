import argparse
import socket
import os
import struct
import hashlib


def main():
    # 1. Configurar o analisador de argumentos
    parser = argparse.ArgumentParser(description="Client para transferência de arquivos usando UDP")
    
    # 2. Adicionar o parâmetro/flag --params
    parser.add_argument('--serverip', type=str, help='IP do servidor')

    # 3. Adicionar o parâmetro/flag --serverport
    parser.add_argument('--serverport', type=int, help='Porta do servidor')

    parser.add_argument('--filename', type=str, help='Nome do arquivo para baixar')

    # 3. Analisar os argumentos da linha de comando
    args = parser.parse_args()
    
    # AF_INET = IPv4 | SOCK_DGRAM = Protocolo UDP 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mensagem = "GET /" + args.filename

    print(f"[*] Enviando para {args.serverip}:{args.serverport} -> '{mensagem}'")

    client_socket.sendto(mensagem.encode('utf-8'), (args.serverip, args.serverport))

    # Aguarda a resposta do servidor
    data, server_address = client_socket.recvfrom(1024)
    print(f"[+] Resposta do servidor {server_address}: {data.decode('utf-8')}")

    # Fecha o socket no cliente
    client_socket.close()

if __name__ == "__main__":
    main()
