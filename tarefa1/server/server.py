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
        data, endereco_client = server_socket.recvfrom(1024)
        
        # Decodifica os bytes recebidos para string
        mensagem = data.decode('utf-8')
        print(f"[+] Mensagem recebida de {endereco_client}: {mensagem}")

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
                        print(f"Arquivo identificado, criando thread para cliente {endereco_client}...")
                        thread = threading.Thread(target=handle_client, args=(endereco_client[0], endereco_client[1], caminho_arquivo))
                        thread.start()
                    else:
                        resposta = f"404 Not Found: arquivo '{nome_arquivo}' nao existe"


def handle_client(client_ip: str, client_port: int, filename: str):
    """
    Thread responsável por gerenciar a transferência de um arquivo específico.
    """

    TAMANHO_CABECALHO = 21

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
                transferir_arquivo(thread_socket, (client_ip, client_port), filename)
                
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

TIPOS_MENSAGEM = {
    b'A': 'ACK',
    b'B': 'START',
    b'D': 'DATA',
    b'E': 'EOF',
}

TAMANHO_CABECALHO_BASICO = struct.calcsize('!cI')

def gerar_mensagem_ack(seq_num: int):
    return struct.pack('!cI', b'A', seq_num)

def gerar_mensagem_comeco_transmissao(seq_num: int):
    mensagem = struct.pack('!cI', b'B', seq_num)
    return mensagem

def gerar_mensagem_dados(seq_num, dados):
    md5_hash = hashlib.md5(dados).digest()  # 16 bytes de hash MD5
    return struct.pack('!cI16s', b'D', seq_num, md5_hash) + dados

def gerar_mensagem_eof(seq_num):
    return struct.pack('!cI16s', b'E', seq_num, b'\x00' * 16)

def tratar_cabecalho(mensagem: bytes):
    """
    Interpreta o cabeçalho

    Retorna um dicionário com o tipo da mensagem, o valor numérico do
    cabeçalho e o payload restante, quando existir.
    """

    if len(mensagem) < TAMANHO_CABECALHO_BASICO:
        raise ValueError(
            f'Mensagem muito curta para conter um cabeçalho válido: '
            f'esperado pelo menos {TAMANHO_CABECALHO_BASICO} bytes, recebido {len(mensagem)}.'
        )

    tipo_bytes, numero = struct.unpack('!cI', mensagem[:TAMANHO_CABECALHO_BASICO])

    if tipo_bytes not in TIPOS_MENSAGEM:
        raise ValueError(f'Tipo de mensagem desconhecido: {tipo_bytes!r}')

    return {
        'tipo': tipo_bytes.decode('ascii'),
        'tipo_nome': TIPOS_MENSAGEM[tipo_bytes],
        'numero': numero,
        'payload': mensagem[TAMANHO_CABECALHO_BASICO:],
    }

def calcular_checksum(dados):
    return hashlib.md5(dados).hexdigest()

def transferir_arquivo(thread_socket: socket.socket, endereco_cliente: tuple, caminho_arquivo: str, timeout_ms: int = 10, max_tentativas: int = 5):
    """
    Função responsável por realizar a transferência do arquivo para o cliente com reenvio automático.
    """
    print(f"[Thread] Iniciando transferência do arquivo '{caminho_arquivo}' para {endereco_cliente}...")

    TAMANHO_PACOTE = 512
    seq_num = 0
    
    # 1. Configura o timeout do socket convertendo milissegundos para segundos
    thread_socket.settimeout(timeout_ms / 1000.0)

    # 2. Correção: leitura em fatias fixas usando bloco 'with' para fechar o arquivo corretamente depois
    with open(caminho_arquivo, 'rb') as arquivo:
        while True:
            # Lê exatamente TAMANHO_PACOTE bytes
            pedaco = arquivo.read(TAMANHO_PACOTE)
            
            # Se a fatia estiver vazia, o arquivo acabou
            if not pedaco:
                break
                
            mensagem_dados = gerar_mensagem_dados(seq_num, pedaco)
            
            ack_confirmado = False
            tentativas = 0

            # 3. Loop de Reenvio: Continua tentando até receber o ACK ou atingir o limite
            while not ack_confirmado and tentativas < max_tentativas:
                thread_socket.sendto(mensagem_dados, endereco_cliente)

                try:
                    # Aguarda a resposta (vai lançar socket.timeout se passar de timeout_ms)
                    data, addr = thread_socket.recvfrom(1024)
                    resposta = tratar_cabecalho(data)

                    if resposta['tipo'] == 'A' and resposta['numero'] == seq_num:
                        # Pacote chegou e foi confirmado!
                        #print(f"[Thread] ACK recebido para seq_num {seq_num}")
                        ack_confirmado = True
                        seq_num += 1
                    else:
                        # Chegou alguma resposta diferente ou um ACK atrasado de um pacote anterior.
                        # Não fazemos break. Apenas ignoramos e deixamos o loop continuar ou estourar o timeout.
                        print(f"[Thread] Resposta ignorada (esperado ACK {seq_num}, recebido: {resposta})")

                except socket.timeout:
                    tentativas += 1
                    print(f"[Thread] Timeout aguardando ACK para seq_num {seq_num}. Reenviando... (Tentativa {tentativas}/{max_tentativas})")

            # Se o loop de tentativas acabou e ainda não confirmou o ACK, abortamos a transferência
            if not ack_confirmado:
                print(f"[Thread] Falha crítica: Conexão instável. Pacote {seq_num} perdido após {max_tentativas} tentativas. Encerrando.")
                return # Abandona a função

    # 4. Envia o pacote de EOF para indicar que terminou a transferência
    mensagem_eof = gerar_mensagem_eof(seq_num)
    thread_socket.sendto(mensagem_eof, endereco_cliente)

    print(f"[Thread] Transferência do arquivo '{caminho_arquivo}' concluída com sucesso!")

    

if __name__ == "__main__":
    main()
