#!/bin/bash

PORT=12345

echo "[*] Iniciando o servidor em background na porta $PORT..."
cd server
python3 server.py --port $PORT &
SERVER_PID=$!

# Aguarda 1 segundo para garantir que o servidor inicializou corretamente
sleep 1

echo "[*] Disparando a requisição do VivaldiWinter.mp4..."
cd ../client

# Executa o cliente em background para podermos matar o servidor enquanto roda
python3 client.py --serverip 127.0.0.1 --serverport $PORT --filename VivaldiWinter.mp4 &
CLIENT_PID=$!

# Deixa a transferência rodar por 1 segundo e meio
echo "[*] Aguardando a transferência iniciar..."
sleep 1.5

echo "[!] ATENÇÃO: Matando o servidor abruptamente no meio da transferência!"
kill -9 $SERVER_PID

echo "[*] Aguardando a reação do cliente (Ele deve estourar o timeout em 5 segundos)..."
wait $CLIENT_PID

echo "[+] Teste de interrupção finalizado."
