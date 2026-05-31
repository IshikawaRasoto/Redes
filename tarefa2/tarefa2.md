# Enunciado


### Implementação de Cliente/Servidor TCP Multithread com Transferência de Arquivos e Chat
---

## Objetivo do Projeto

Desenvolver uma aplicação cliente-servidor utilizando o protocolo TCP e programação de sockets. O servidor deve lidar com múltiplos clientes simultaneamente (multithreading) e oferecer transferência de arquivos com verificação de integridade (SHA) e um serviço de chat.

### Exemplos de Partida (Hello World)

> **Dica:** Para se familiarizar com a API de sockets e Threads, sugere-se iniciar com exemplos básicos de cada linguagem:
> * **Python:** [Socket Programming in Python](https://realpython.com/python-sockets/)
> * **Java:** [A Guide to Java Sockets](https://www.baeldung.com/a-guide-to-java-sockets)
> * **C:** [TCP Server-Client in C](https://www.geeksforgeeks.org/tcp-server-client-implementation-in-c/)
> * **C++:** [Socket Programming in C/C++](https://www.geeksforgeeks.org/socket-programming-cc/)

> **Restrição Técnica:** É obrigatório utilizar a API de sockets diretamente. Não é permitido o uso de bibliotecas que abstraiam a manipulação de conexões TCP.

## Requisitos de Manipulação de Arquivos

Ao implementar a funcionalidade de transferência de arquivos, o aluno deve se atentar obrigatoriamente a:
* **Verificação de Existência:** O servidor deve validar se o arquivo solicitado existe antes de iniciar a transferência, enviando um erro padronizado caso contrário.
* **Diretório Padrão:** O servidor deve apenas servir arquivos localizados em um diretório específico (ex: pasta `/arquivos`).

> **ALERTA DE SEGURANÇA (Path Injection / Traversal):**
> Um erro comum e extremamente explorado por atacantes é a falta de validação do nome do arquivo enviado pelo usuário. Se o seu servidor apenas concatena o que o usuário envia ao caminho da pasta (ex: `./arquivos/` + `entrada_usuario`), um atacante pode enviar strings como `../../etc/passwd` ou `../../windows/system32/config/SAM` para acessar qualquer arquivo do seu sistema operacional. 
> **O seu código deve sanitizar a entrada para impedir que o usuário saia do diretório padrão.**

## Requisitos do Servidor TCP (Multithread)

* **Gerenciamento de Conexões:** Aceitar conexões e, para cada cliente (`accept`), **criar uma thread dedicada**.
* **Funcionalidades da Thread:**
    * Loop de recepção de comandos (Sair, Arquivo, Chat).
    * Cálculo de Hash SHA-256 em tempo real (lendo em chunks para eficiência).
    * Envio de mensagens de chat iniciadas pelo servidor (Broadcast para os clientes).

## Requisitos do Cliente TCP

* **Interface:** Menu interativo (Sair, Arquivo, Chat).
* **Integridade:** Comparar o SHA recebido do servidor com o SHA calculado localmente após o download.
* **Concorrência no Cliente:** O cliente deve ser capaz de receber mensagens de chat mesmo enquanto aguarda uma entrada de teclado do usuário.

> **Roteiro para Vídeo de Apresentação**
> * **REGRA CRÍTICA:** O código mostrado no vídeo **NÃO PODE TER COMENTÁRIOS**. O aluno deve explicar a lógica verbalmente. Código com comentários que auxiliem a leitura da explicação resultará em penalização.
> * **Envio:** Link do **YouTube** (máximo **5 min**) e arquivo **.ZIP** no Classroom.

### Itens Obrigatórios a Demonstrar e Explicar

> **Critérios de Avaliação (Demonstração e Explicação Técnica):**
>
> * **Multithreading e Chat Bidirecional (2,5 pts):** >   1. Demonstração do servidor atendendo dois clientes simultaneamente.
>   2. O cliente deve ser capaz de receber mensagens de chat do servidor (broadcast) mesmo enquanto aguarda o usuário digitar um comando (uso de threads no cliente).
>
> * **Protocolo, Framing e Arquivos Grandes (2,5 pts):** >   1. Demonstração da transferência bem-sucedida de um arquivo **> 10 MB**.
>   2. Explicação técnica de como o código segmenta o arquivo e como o protocolo separa os comandos/metadados dos dados brutos no stream TCP.
>
> * **Segurança de Diretório (2,5 pts):** >   1. Demonstração do tratamento para arquivos inexistentes e proteção contra Path Traversal (bloqueio de acesso fora da pasta raiz). O servidor deve recusar requisições que tentem acessar arquivos fora da pasta raiz (ex: usando `../../`).
>
> * **Integridade via SHA-256 (2,5 pts):** >   1. Demonstração do cálculo de Hash SHA no servidor e a validação automática no cliente após a recepção do arquivo grande. 
>   2. Explicar como o cálculo é feito em pedaços (chunks) para não estourar a memória RAM.

## Dicas Técnicas

> **Para o Chat bidirecional no Cliente**, você provavelmente precisará de uma thread para ler o teclado e outra para ler o socket simultaneamente, evitando que o programa fique travado esperando o usuário digitar.

> **O Problema do Stream TCP:**
> Lembre-se que o TCP não preserva os limites das mensagens. Se você enviar o “Nome do Arquivo” e o “Conteúdo” em dois comandos `send()` seguidos, eles podem chegar colados no receptor. 
> **Sugestão:** Implemente um cabeçalho inicial de tamanho fixo que informe ao receptor quantos bytes ele deve ler para o comando e quantos para os dados.

> **Cálculo de SHA em Arquivos Grandes:**
> Para arquivos acima de 10MB, evite ler o arquivo inteiro para a memória. Leia-o em blocos (ex: 4KB ou 8KB), alimentando o algoritmo de Hash gradualmente antes de enviar os bytes pelo socket.

### Referências

* [Documentação Sockets (Python)](https://docs.python.org/3/library/socket.html) / [Java Sockets](https://docs.oracle.com/javase/8/docs/api/java/net/Socket.html)
* [Biblioteca Hashlib (Cálculo de SHA)](https://docs.python.org/3/library/hashlib.html)
* [OWASP: Path Traversal Attack (Explicação Técnica)](https://owasp.org/www-community/attacks/Path_Traversal)

---
*Fonte: Prof. Mauro Fonseca - UTFPR - DAINF | Última modificação: 30/04/2026*