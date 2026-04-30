#!/bin/bash

PORT=12345

echo "[*] Iniciando o servidor em background na porta $PORT..."
cd server
python3 server.py --port $PORT &
SERVER_PID=$!

sleep 1

echo "[*] Disparando requisição do Video.mp4 com SIMULAÇÃO DE PERDA DE PACOTES..."
cd ../client

python3 client.py --serverip 127.0.0.1 --serverport $PORT --filename Video.mp4 --simulate_loss

echo "[+] Transferência com perda de pacotes concluída."

echo "[*] Derrubando o servidor."
kill $SERVER_PID
echo "[+] Teste finalizado."
