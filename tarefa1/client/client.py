import argparse
import socket
import os
import struct
import hashlib


def main():

    parser = argparse.ArgumentParser(description="Client para transferência de arquivos usando UDP")
    
    parser.add_argument('--serverip', type=str, help='IP do servidor')
    parser.add_argument('--serverport', type=int, help='Porta do servidor')
    parser.add_argument('--filename', type=str, help='Nome do arquivo para baixar')
    parser.add_argument('--simulate_loss', action='store_true', help='Simular perda de pacotes (opcional)')

    args = parser.parse_args()

    if args.simulate_loss:
        print("Simulação de perda de pacotes ativada. Alguns pacotes serão ignorados segundo arquivo de config.")
        arquivo_perda = "sim.txt"
        if not os.path.isfile(arquivo_perda):
            print(f"Arquivo de configuração para simulação de perda '{arquivo_perda}' não encontrado. Encerrando.")
            return
        simular_perda = True
    else:
        simular_perda = False

    
    # AF_INET = IPv4 | SOCK_DGRAM = Protocolo UDP 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    mensagem = "GET /" + args.filename

    print(f"[*] Enviando para {args.serverip}:{args.serverport} -> '{mensagem}'")

    client_socket.sendto(mensagem.encode('utf-8'), (args.serverip, args.serverport))

    # Aguarda a resposta do servidor
    data, endereco_servidor = client_socket.recvfrom(1024)
    print(f"[+] Resposta do servidor IP:{endereco_servidor[0]} PORT:{endereco_servidor[1]}: {data.decode('utf-8')}")

    mensagem = "ACK_START"

    client_socket.sendto(mensagem.encode('utf-8'), (endereco_servidor[0], endereco_servidor[1]))

    receber_arquivo(client_socket, endereco_servidor, args.filename, simular_perda, arquivo_perda if simular_perda else None)

    # Fecha o socket no cliente
    client_socket.close()


def receber_arquivo(client_socket: socket.socket, endereco_servidor: tuple, filename: str, simular_perda: bool = False, arquivo_perda: str = "sim.txt"):
    # Implementar a lógica para receber o arquivo em blocos e salvar localmente

    fatias_recebidas = {}
    contagem_pacotes_ignorados = 0
    
    try:
        while True:
            # Recebe o pacote do remetente
            pacote_recebido, endereco = client_socket.recvfrom(1024)
            
            # Decodifica o pacote recebido para extrair os dados
            mensagem_decodificada = decodificar_mensagem_dados(pacote_recebido)

            # Verifica o tipo da mensagem (D para dados, E para EOF)
            if mensagem_decodificada['tipo'] == b'D':
                # Se for uma mensagem de dados, armazena a fatia recebida
                #print(f"Recebido pacote de dados: Seq={mensagem_decodificada['sequencia']} Integro={mensagem_decodificada['integro']}")
                if mensagem_decodificada['integro']:
                    #print(f"Pacote com sequência {mensagem_decodificada['sequencia']} recebido com integridade. Armazenando e enviando ACK.")
                    if mensagem_decodificada['sequencia'] not in fatias_recebidas:
                        if simular_perda:
                            with open(arquivo_perda, 'r') as f:
                                linhas = f.readlines()
                                if contagem_pacotes_ignorados < 3 and str(mensagem_decodificada['sequencia']) + '\n' in linhas:
                                    print(f"Simulando perda do pacote de sequência {mensagem_decodificada['sequencia']}. Ignorando.")
                                    contagem_pacotes_ignorados += 1
                                    continue
                        #print(f"Armazenando pacote de sequência {mensagem_decodificada['sequencia']}...")
                        fatias_recebidas[mensagem_decodificada['sequencia']] = mensagem_decodificada['dados']
                        client_socket.sendto(gerar_mensagem_ack(mensagem_decodificada['sequencia']), endereco)
                        ultimo_pacote_recebido = mensagem_decodificada['sequencia']
                        contagem_pacotes_ignorados = 0  # Reseta a contagem de pacotes ignorados após receber um pacote válido
                    else:
                        client_socket.sendto(gerar_mensagem_ack(ultimo_pacote_recebido), endereco)
                        print(f"Pacote com sequência {mensagem_decodificada['sequencia']} já recebido. Ignorando.")
                else:
                    print(f"Pacote com sequência {mensagem_decodificada['sequencia']} corrompido. Ignorando.")
            elif mensagem_decodificada['tipo'] == b'E':
                # Se for uma mensagem de EOF, encerra a recepção
                print("Pacote EOF recebido. Encerrando recepção.")
                break
            
            
    except socket.timeout:
        # Quando o socket fica 5 segundos sem receber nada, ele cai aqui
        print("\nTimeout atingido. Assumindo fim da transmissão.")

    # Se não recebemos nada, encerra a função
    if not fatias_recebidas:
        print("Nenhum dado foi recebido.")
        return

    # --- FASE DE RECONSTRUÇÃO ---
    print(f"Reconstruindo arquivo com {len(fatias_recebidas)} pacotes...")

    caminho_salvamento = os.path.join(os.getcwd(), "arquivo_recebido_" + filename)
    
    # Abre o arquivo final em modo de escrita binária ('wb')
    with open(caminho_salvamento, 'wb') as arquivo_final:
        # Pulo do gato: ordenar as chaves para garantir a sequência correta (0, 1, 2, 3...)
        para_escrever = sorted(fatias_recebidas.keys())
        
        # Verifica se houve perda de pacotes (opcional, mas recomendado para debug)
        pacote_maximo = para_escrever[-1]
        if len(para_escrever) - 1 != pacote_maximo:
            print(f"ALERTA: Ocorreu perda de pacotes! Recebidos {len(para_escrever)}, esperado {pacote_maximo + 1}.")
        
        # Escreve as fatias na ordem no arquivo final
        for seq in para_escrever:
            arquivo_final.write(fatias_recebidas[seq])
            
    print(f"Arquivo salvo com sucesso em: {caminho_salvamento}")

def decodificar_mensagem_dados(pacote_recebido):
    # 1. Define o formato e calcula o tamanho dinamicamente (21 bytes)
    formato_cabecalho = '!cI16s'
    tamanho_cabecalho = struct.calcsize(formato_cabecalho)
    
    # Validação básica de tamanho para evitar erros se o pacote vier corrompido/menor
    if len(pacote_recebido) < tamanho_cabecalho:
        raise ValueError("Pacote muito pequeno, cabeçalho incompleto.")

    # 2. Fatiamos o pacote recebido em duas partes: Cabeçalho e Dados
    cabecalho = pacote_recebido[:tamanho_cabecalho]
    dados = pacote_recebido[tamanho_cabecalho:]
    
    # 3. Desempacotamos o cabeçalho
    # Retorna uma tupla: (b'D', 123, b'hash_de_16_bytes...')
    tipo_msg, seq_num, md5_recebido = struct.unpack(formato_cabecalho, cabecalho)
    
    # 4. Verificação de Integridade (Checksum)
    # Recalculamos o MD5 com os dados que acabaram de chegar
    md5_calculado = hashlib.md5(dados).digest()
    
    # Se os hashes não baterem, o pacote foi corrompido na rede
    dados_integros = (md5_recebido == md5_calculado)
    
    return {
        'tipo': tipo_msg,           # Idealmente será b'D'
        'sequencia': seq_num,       # O número da fatia
        'integro': dados_integros,  # True se o arquivo chegou perfeito, False se corrompeu
        'dados': dados              # O binário da fatia do arquivo
    }

def gerar_mensagem_ack(seq_num):
    return struct.pack('!cI', b'A', seq_num)

if __name__ == "__main__":
    main()
