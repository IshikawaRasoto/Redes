# Tarefa 1 

Aluno: Rafael Eijy Ishikawa Rasoto
RA: 2004585

A tarefa 1 tem como objetivo desenvolver um protocolo de comunicação sobre o UDP para transferência de arquivos que atinja requisitos descritos pelo professor no documento: https://pessoal.dainf.ct.utfpr.edu.br/maurofonseca/doku.php?id=cursos:icsr30:trab2

## Protocolo

O protocolo o qual desenvolverei será simples, consistindo em um pequeno handshake no início de três estapas antes de iniciar a transferência do arquivo. 

1. O client enviará para o servidor uma requisição GET com o nome do arquivo desejado
2. O servidor verificará a sintaxo do pedido e a existência do arquivo e, com base nisso:
    2.1. Se a sintaxe estiver incorreta, retornará um erro especificando esse problema
    2.2. Se a sintaxe estiver correta mas o arquivo não existir, retornará um erro especificando esse problema
    2.3. Se a sintaxe estiver correta e o arquivo existir, seguirá para o terceiro passo
3. O servidor instanciará uma thread para transferência do arquivo para aquele request em específico se:
    3.1. Aquele client não estiver fazendo uma transferência no momento (evitar duplicação para o mesmo client).
4. A nova thread criará um novo socket UDP com uma porta aleatória e instanciada um código de Ack para o cliente indicando que o request foi corretamente recebido.
5. O Client deve enviar um cabeçalho requisitando o início da transferência.
6. A thread do servidor ao receber esse cabeçalho, sabe que foram feitas 3 trocas de informações e que o client está ciente da troca de porta.
7. A thread do servidor irá fatiar o arquivo original em n pedaços (segmentos), garantindo que o tamanho de cada datagrama (payload + cabeçalho) fique sempre inferior ao limite do MTU da rede, evitando a fragmentação excessiva a nível de IP.
8. Para cada segmento enviado, o servidor incluirá um cabeçalho customizado contendo as seguintes informações de controle:
    8.1. Tipo de mensagem: Identificador da função do pacote (Início da transmissão, Dados, ACK, EOF)
    8.2. Número de sequência: Identificador numérico crescente para garantir a ordenação do cliente e detecção de perdas
    8.3. Hash MD5
9. Ao finalizar o envio do arquivo, a thread será desinstanciada pelo servidor, encerrando a conexão.
