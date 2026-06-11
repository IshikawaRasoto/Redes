# Aluno: Rafael Eijy Ishikawa Rasoto
# Trabalho 2 - Redes de Computadores UTFPR

import struct
import socket

# Formato do cabeçalho TCP: !cI
# ! - Network byte order
# c - 1 byte char (Tipo de mensagem)
# I - 4 bytes unsigned int (Tamanho do payload)
FORMATO_CABECALHO = '!cI'
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

# Tipos de mensagens do protocolo
TIPOS_MENSAGEM = {
    b'C': 'CHAT',       # Mensagem de chat
    b'G': 'GET',        # Requisição de arquivo
    b'S': 'FILE_START', # Início de envio de arquivo (tamanho|sha256)
    b'D': 'FILE_DATA',  # Bloco de dados do arquivo
    b'F': 'FILE_EOF',   # Fim da transmissão do arquivo
    b'X': 'ERROR',      # Mensagem de erro
    b'E': 'EXIT'        # Solicitação de saída
}

def ler_exato(sock: socket.socket, n: int) -> bytes:
    """
    Lê exatamente n bytes do socket TCP. Lida com fragmentação e garante
    que o buffer retornado tenha o tamanho solicitado, a menos que a conexão
    seja encerrada prematuramente.
    """
    dados = b''
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão fechada pelo peer remoto.")
        dados += pacote
    return dados

def receber_mensagem(sock: socket.socket) -> tuple[bytes, bytes]:
    """
    Recebe uma mensagem TCP completa, lendo primeiro o cabeçalho de 5 bytes
    e depois o payload correspondente de tamanho dinâmico.
    """
    cabecalho = ler_exato(sock, TAMANHO_CABECALHO)
    tipo_msg, tamanho_payload = struct.unpack(FORMATO_CABECALHO, cabecalho)
    
    if tipo_msg not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem inválido ou corrompido: {tipo_msg}")
        
    payload = ler_exato(sock, tamanho_payload)
    return tipo_msg, payload

def enviar_mensagem(sock: socket.socket, tipo: bytes, payload: bytes = b''):
    """
    Envia uma mensagem TCP completa contendo cabeçalho de 5 bytes e payload.
    Utiliza sendall para garantir que todo o bloco seja enviado.
    """
    if tipo not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem inválido: {tipo}")
        
    cabecalho = struct.pack(FORMATO_CABECALHO, tipo, len(payload))
    sock.sendall(cabecalho + payload)
