import struct
import socket

FORMATO_CABECALHO = '!cI'
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

TIPOS_MENSAGEM = {
    b'C': 'CHAT',
    b'G': 'GET',
    b'S': 'FILE_START',
    b'D': 'FILE_DATA',
    b'F': 'FILE_EOF',
    b'X': 'ERROR',
    b'E': 'EXIT'
}

def ler_exato(sock: socket.socket, n: int) -> bytes:
    dados = b''
    while len(dados) < n:
        pacote = sock.recv(n - len(dados))
        if not pacote:
            raise ConnectionError("Conexão fechada pelo peer remoto.")
        dados += pacote
    return dados

def receber_mensagem(sock: socket.socket) -> tuple[bytes, bytes]:
    cabecalho = ler_exato(sock, TAMANHO_CABECALHO)
    tipo_msg, tamanho_payload = struct.unpack(FORMATO_CABECALHO, cabecalho)
    
    if tipo_msg not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem inválido ou corrompido: {tipo_msg}")
        
    payload = ler_exato(sock, tamanho_payload)
    return tipo_msg, payload

def enviar_mensagem(sock: socket.socket, tipo: bytes, payload: bytes = b''):
    if tipo not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem inválido: {tipo}")
        
    cabecalho = struct.pack(FORMATO_CABECALHO, tipo, len(payload))
    sock.sendall(cabecalho + payload)
