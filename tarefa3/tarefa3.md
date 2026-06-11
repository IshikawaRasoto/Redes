# Trabalho com conexão TCP - Parte 2 - Trabalho 3

### HTTP/TCP - Servidor Web Multithreads
---

## O Protocolo de Controle de Transmissão - TCP

Neste trabalho iremos continuar explorando a implementação de uma aplicação rodando sobre *TCP* através da programação com *sockets*. Este trabalho tem a finalidade de trazer o conhecimento de programação e funcionamento básico do protocolo *TCP*, demonstrando os serviços que o *TCP* fornece para a camada de aplicação. Baseado no trabalho anterior, iremos transformar o servidor em um **Servidor HTTP simplificado**. 

> **Importante:** É **obrigatório** que este trabalho use o **Trabalho 2** (Servidor Multithread) como base de código.

### Fluxo do Trabalho

1. **Preparação do Servidor:**
   * Use o código do servidor TCP multithread anterior.
   * Mantenha a restrição: **não use bibliotecas de alto nível**; manipule os sockets TCP diretamente pela API do SO/Linguagem.
   * O servidor deve ser executado primeiro, aguardando conexões em porta > 1024.
2. **Processamento na Thread:**
   * Para cada conexão aceita, crie uma thread dedicada.
   * A thread deve ler os dados enviados pelo Browser e realizar o **parsing da requisição HTTP**.
   * Exemplo de entrada esperada: `GET /pagina.html HTTP/1.1`
3. **Uso do Cliente (Browser):**
   * O cliente será o navegador de sua preferência (Chrome, Firefox, etc.).
   * O teste consiste em digitar a URL: `http://[IP_do_Servidor]:[Porta]/arquivo.html`.
   * O servidor deve responder com o cabeçalho HTTP correto seguido pelo conteúdo do arquivo.

> **Roteiro para Vídeo de Apresentação**
> * **Parte 1:** Mostrar todos os itens obrigatórios funcionando (demonstração prática no browser).
> * **Parte 2:** Explicar a implementação navegando pelo código fonte.
> * **REGRA CRÍTICA:** O código mostrado no vídeo **NÃO PODE TER COMENTÁRIOS**. O aluno deve explicar a lógica verbalmente, demonstrando domínio total do código. Caso o código contenha comentários que auxiliem a leitura da explicação, o trabalho será penalizado.
> * **NÃO** envie o arquivo do vídeo! Envie o link do **YouTube** nos comentários particulares do Classroom.
> * O vídeo deve ter no máximo **5 min**.
> * Colocar no Classroom um arquivo **.ZIP** com todo o código fonte (neste arquivo o uso de comentários é livre para documentação).

### Itens Obrigatórios a Demonstrar e Explicar

> **Critérios de Avaliação e Itens Técnicos (Apresentação sem leitura de comentários):**

**Multithreading e Concorrência (2,0 pts):**
1. Demonstrar o servidor atendendo pelo menos duas abas (ou recursos) do navegador simultaneamente, sem que uma conexão bloqueie a outra.
2. Explicar como o loop principal delega o socket para a thread e como o estado da conexão é mantido.

**Exibição de Mídia e Tratamento Binário (2,0 pts):**
1. O navegador deve renderizar com sucesso arquivos **HTML e imagens JPEG/PNG**.
2. O aluno deve explicar a diferença técnica no código entre o envio de texto (HTML) e o envio de dados binários (imagens), garantindo que não haja corrupção de bytes.

**Cabeçalhos HTTP e Inspeção de Protocolo (2,0 pts):**
1. Demonstrar via aba **Rede (Network)** do Browser o recebimento correto de:
   * `HTTP/1.x 200 OK` (sucesso) ou códigos de erro pertinentes.
   * `Content-Type` (configurado dinamicamente conforme a extensão do arquivo).
   * `Content-Length` (valor exato do tamanho do arquivo em bytes).

**Tratamento de Erro 404 (2,0 pts):**
1. Quando o arquivo solicitado não existir, o Browser deve exibir uma página HTML de erro enviada pelo servidor.
2. O aluno deve mostrar no código a lógica de verificação de existência de arquivo e a montagem da resposta de erro.

**Segurança Básica e Robustez (2,0 pts):**
1. Explicar e demonstrar como o servidor impede que o cliente acesse arquivos fora da pasta raiz (ex: via ataque de injeção de caminho como `../../arquivo_do_sistema`).
2. O servidor deve sanitizar o caminho solicitado para garantir o isolamento do diretório padrão.

> **Como demonstrar os Cabeçalhos HTTP no vídeo:**
> 1. No navegador, pressione **F12** (ou clique com o botão direito e selecione "Inspecionar").
> 2. Vá até a aba **Rede** (ou **Network**).
> 3. Recarregue a página (**F5**).
> 4. Clique no nome do arquivo (ex: `pagina.html`) que aparecer na lista.
> 5. No painel que abrir, procure pela seção **Headers** (Cabeçalhos) e localize os **Response Headers** (Cabeçalhos de Resposta). São esses os dados que o seu servidor enviou!

> **Dica extra:** O Browser faz requisições automáticas para ícones (favicon.ico). Seu servidor deve estar pronto para tratar essas múltiplas conexões de forma assíncrona/concorrente.

## Dicas e Exemplos Auxiliares

> **A importância do Content-Length:**
> É obrigatório o envio do cabeçalho `Content-Length`. Sem ele, o navegador não sabe quantos bytes esperar e manterá a conexão em aberto (loading infinito) até que ocorra um timeout ou a conexão seja encerrada abruptamente. O valor deve ser o tamanho exato do corpo da mensagem (o arquivo) em bytes.

