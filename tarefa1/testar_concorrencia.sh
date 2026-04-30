#!/bin/bash

# Define a porta que será usada no teste
PORT=12345

echo "[*] Iniciando o servidor em background na porta $PORT..."
cd server
python3 server.py --port $PORT &
SERVER_PID=$!

# Aguarda um segundo para garantir que o servidor inicializou corretamente
sleep 1

echo "[*] Disparando requisições simultâneas..."
cd ../client

# Dispara o primeiro cliente rodando em background
echo " -> Cliente 1 requisitando 'VivaldiWinter.mp4'"
python3 client.py --serverip 127.0.0.1 --serverport $PORT --filename VivaldiWinter.mp4 &
CLIENT1_PID=$!

# Dispara o segundo cliente rodando em background
echo " -> Cliente 2 requisitando 'VivaldiSummer.mp4'"
python3 client.py --serverip 127.0.0.1 --serverport $PORT --filename VivaldiSummer.mp4 &
CLIENT2_PID=$!

# Aguarda o término da execução de ambos os clientes
wait $CLIENT1_PID
echo "[+] Cliente 1 finalizou o download."

wait $CLIENT2_PID
echo "[+] Cliente 2 finalizou o download."

echo "[*] Ambas transferências concluídas. Derrubando o servidor."
kill $SERVER_PID
echo "[+] Teste de concorrência finalizado com sucesso."
