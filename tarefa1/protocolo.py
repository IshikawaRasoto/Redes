# Aluno: Rafael Eijy Ishikawa Rasoto
# Trabalho 1 - Redes de Computadores UTFPR

import struct
import hashlib

# Formato do cabeçalho: !c16sI
# !   - Network byte order
# c   - 1 byte char (Tipo)
# 16s - 16 bytes string (MD5 Hash)
# I   - 4 bytes unsigned int (Sequence Number)
FORMATO_CABECALHO = '!c16sI'
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)

TIPOS_MENSAGEM = {
    b'A': 'ACK',
    b'B': 'START',
    b'D': 'DATA',
    b'E': 'EOF',
    b'G': 'GET',
    b'X': 'ERROR'
}

def calcular_hash_dados(seq_num: int, dados: bytes) -> bytes:
    """
    O hash é aplicado tanto para o número de sequência quanto para o dado
    que vem posteriormente.
    """
    seq_bytes = struct.pack('!I', seq_num)
    return hashlib.md5(seq_bytes + dados).digest()

def gerar_pacote(tipo: bytes, seq_num: int, dados: bytes = b'') -> bytes:
    """
    Gera um pacote completo com cabeçalho e dados.
    """
    if tipo not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem inválido: {tipo}")
        
    md5_hash = calcular_hash_dados(seq_num, dados)
    cabecalho = struct.pack(FORMATO_CABECALHO, tipo, md5_hash, seq_num)
    return cabecalho + dados

def desempacotar_pacote(pacote_recebido: bytes) -> dict:
    """
    Extrai as informações do pacote recebido e valida sua integridade.
    """
    if len(pacote_recebido) < TAMANHO_CABECALHO:
        raise ValueError(f"Pacote muito pequeno. Esperado pelo menos {TAMANHO_CABECALHO} bytes, recebido {len(pacote_recebido)}.")
        
    cabecalho = pacote_recebido[:TAMANHO_CABECALHO]
    dados = pacote_recebido[TAMANHO_CABECALHO:]
    
    tipo_msg, md5_recebido, seq_num = struct.unpack(FORMATO_CABECALHO, cabecalho)
    
    if tipo_msg not in TIPOS_MENSAGEM:
        raise ValueError(f"Tipo de mensagem desconhecido: {tipo_msg}")
        
    md5_calculado = calcular_hash_dados(seq_num, dados)
    integro = (md5_recebido == md5_calculado)
    
    return {
        'tipo': tipo_msg,
        'tipo_nome': TIPOS_MENSAGEM[tipo_msg],
        'sequencia': seq_num,
        'integro': integro,
        'dados': dados
    }
