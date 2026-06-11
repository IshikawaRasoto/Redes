#!/bin/bash

PORT=12346

echo "[*] Iniciando o servidor em background na porta $PORT..."
cd server
python3 server.py --port $PORT &
SERVER_PID=$!

sleep 1

echo "[*] Testando proteções contra Path Traversal e arquivos inexistentes..."
cd ../client

echo " -> Tentando acessar arquivo inexistente 'nao_existe.txt'"
(echo "2"; echo "nao_existe.txt"; sleep 2; echo "3") | python3 client.py --serverip 127.0.0.1 --serverport $PORT > error1.log 2>&1

echo " -> Tentando acessar fora da raiz usando Path Traversal '../../server.py'"
(echo "2"; echo "../../server.py"; sleep 2; echo "3") | python3 client.py --serverip 127.0.0.1 --serverport $PORT > error2.log 2>&1

echo "[*] Derrubando o servidor..."
kill $SERVER_PID
echo "[+] Teste de segurança finalizado."

echo ""
echo "=== RESPOSTA PARA ARQUIVO INEXISTENTE ==="
cat error1.log | grep -i "Erro do Servidor" || cat error1.log

echo ""
echo "=== RESPOSTA PARA PATH TRAVERSAL ==="
cat error2.log | grep -i "Erro do Servidor" || cat error2.log
