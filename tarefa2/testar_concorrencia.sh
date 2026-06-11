#!/bin/bash

PORT=12345

echo "[*] Iniciando o servidor em background na porta $PORT..."
cd server
python3 server.py --port $PORT &
SERVER_PID=$!

sleep 1

echo "[*] Disparando requisições simultâneas..."
cd ../client

echo " -> Cliente 1 requisitando 'Video.mp4'"
(echo "2"; echo "Video.mp4"; sleep 5; echo "3") | python3 client.py --serverip 127.0.0.1 --serverport $PORT > client1.log 2>&1 &
CLIENT1_PID=$!

echo " -> Cliente 2 requisitando 'teste.txt'"
(echo "2"; echo "teste.txt"; sleep 5; echo "3") | python3 client.py --serverip 127.0.0.1 --serverport $PORT > client2.log 2>&1 &
CLIENT2_PID=$!

wait $CLIENT1_PID
echo "[+] Cliente 1 finalizou."

wait $CLIENT2_PID
echo "[+] Cliente 2 finalizou."

echo "[*] Ambas transferências concluídas. Derrubando o servidor."
kill $SERVER_PID
echo "[+] Teste de concorrência finalizado com sucesso."

echo ""
echo "=== LOG DO CLIENTE 1 (Video.mp4) ==="
cat client1.log | grep -A 4 "Verificando hash" || cat client1.log

echo ""
echo "=== LOG DO CLIENTE 2 (teste.txt) ==="
cat client2.log | grep -A 4 "Verificando hash" || cat client2.log
