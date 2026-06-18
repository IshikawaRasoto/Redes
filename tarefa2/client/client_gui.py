import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
import hashlib

from client import TCPClient

BG_DARK = "#1e1e2e"
BG_LIGHT = "#313244"
FG_LIGHT = "#cdd6f4"
FG_SUB = "#a6adc8"
ACCENT = "#cba6f7"
ACCENT_GREEN = "#a6e3a1"
ACCENT_RED = "#f38ba8"
ACCENT_BLUE = "#89b4fa"

def make_button(parent, text, command, bg_color=ACCENT, fg_color=BG_DARK):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg=fg_color,
        activebackground=fg_color,
        activeforeground=bg_color,
        font=("Helvetica", 10, "bold"),
        relief="flat",
        bd=0,
        padx=10,
        pady=5
    )
    def on_enter(e):
        if btn['state'] == 'normal':
            btn.config(bg=fg_color, fg=bg_color)
    def on_leave(e):
        if btn['state'] == 'normal':
            btn.config(bg=bg_color, fg=fg_color)
            
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

class ClientGUI:
    def __init__(self, root):
        self.root = root
        
        self.client = TCPClient(
            on_chat=lambda msg: self.root.after(0, self._handle_chat_message, msg),
            on_download_start=lambda filename, size, sha: self.root.after(0, self._handle_download_start, filename, size, sha),
            on_download_chunk=lambda received, total: self.root.after(0, self._update_download_progress, received, total),
            on_download_eof=lambda filename, sha: self.root.after(0, self._handle_download_eof, filename, sha),
            on_error=lambda msg: self.root.after(0, self._handle_server_error, msg),
            on_conn_lost=lambda: self.root.after(0, self._handle_connection_lost)
        )
        
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Cliente TCP - Chat & Transferência de Arquivos")
        self.root.geometry("850x570")
        self.root.configure(bg=BG_DARK)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        
        self.conn_frame = tk.Frame(self.root, bg=BG_DARK, pady=10, padx=15)
        self.conn_frame.grid(row=0, column=0, sticky="ew")
        
        self.lbl_ip = tk.Label(self.conn_frame, text="IP Servidor:", bg=BG_DARK, fg=FG_LIGHT, font=("Helvetica", 10, "bold"))
        self.lbl_ip.pack(side="left", padx=5)
        
        self.ent_ip = tk.Entry(self.conn_frame, bg=BG_LIGHT, fg=FG_LIGHT, insertbackground=FG_LIGHT, relief="flat", font=("Helvetica", 10), width=15)
        self.ent_ip.insert(0, "127.0.0.1")
        self.ent_ip.pack(side="left", padx=5)
        
        self.lbl_port = tk.Label(self.conn_frame, text="Porta:", bg=BG_DARK, fg=FG_LIGHT, font=("Helvetica", 10, "bold"))
        self.lbl_port.pack(side="left", padx=5)
        
        self.ent_port = tk.Entry(self.conn_frame, bg=BG_LIGHT, fg=FG_LIGHT, insertbackground=FG_LIGHT, relief="flat", font=("Helvetica", 10), width=8)
        self.ent_port.insert(0, "12345")
        self.ent_port.pack(side="left", padx=5)
        
        self.btn_connect = make_button(self.conn_frame, "Conectar", self.toggle_connection, bg_color=ACCENT_BLUE)
        self.btn_connect.pack(side="left", padx=15)
        
        self.lbl_status = tk.Label(self.conn_frame, text="● Desconectado", bg=BG_DARK, fg=ACCENT_RED, font=("Helvetica", 10, "bold"))
        self.lbl_status.pack(side="right", padx=10)
        
        self.sep = tk.Frame(self.root, height=1, bg=BG_LIGHT)
        self.sep.grid(row=0, column=0, sticky="ews")
        
        self.main_frame = tk.Frame(self.root, bg=BG_DARK, padx=15, pady=10)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.rowconfigure(0, weight=1)
        
        self.chat_frame = tk.Frame(self.main_frame, bg=BG_DARK)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.chat_frame.rowconfigure(0, weight=0)
        self.chat_frame.rowconfigure(1, weight=1)
        self.chat_frame.rowconfigure(2, weight=0)
        self.chat_frame.columnconfigure(0, weight=1)
        
        lbl_chat_title = tk.Label(self.chat_frame, text="CHAT DE TRANSMISSÃO (BROADCAST)", bg=BG_DARK, fg=ACCENT, font=("Helvetica", 11, "bold"))
        lbl_chat_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.chat_history = scrolledtext.ScrolledText(
            self.chat_frame, bg=BG_LIGHT, fg=FG_LIGHT, insertbackground=FG_LIGHT,
            relief="flat", font=("Helvetica", 10), state="disabled", wrap="word",
            highlightthickness=1, highlightbackground=BG_LIGHT, highlightcolor=BG_LIGHT
        )
        self.chat_history.grid(row=1, column=0, sticky="nsew", pady=5)
        
        self.chat_history.tag_configure("system", foreground=FG_SUB, font=("Helvetica", 9, "italic"))
        self.chat_history.tag_configure("error", foreground=ACCENT_RED, font=("Helvetica", 10, "bold"))
        self.chat_history.tag_configure("me", foreground=ACCENT_BLUE, font=("Helvetica", 10, "bold"))
        self.chat_history.tag_configure("server", foreground=ACCENT_GREEN, font=("Helvetica", 10, "bold"))
        self.chat_history.tag_configure("other", foreground=ACCENT, font=("Helvetica", 10, "bold"))
        
        self.chat_input_frame = tk.Frame(self.chat_frame, bg=BG_DARK)
        self.chat_input_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        self.chat_input_frame.columnconfigure(0, weight=1)
        
        self.ent_msg = tk.Entry(
            self.chat_input_frame, bg=BG_LIGHT, fg=FG_LIGHT, insertbackground=FG_LIGHT,
            relief="flat", font=("Helvetica", 10), highlightthickness=1,
            highlightbackground=BG_LIGHT, highlightcolor=ACCENT
        )
        self.ent_msg.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 5))
        self.ent_msg.bind("<Return>", lambda e: self.send_chat_message())
        self.ent_msg.config(state="disabled")
        
        self.btn_send = make_button(self.chat_input_frame, "Enviar", self.send_chat_message, bg_color=ACCENT)
        self.btn_send.grid(row=0, column=1, sticky="ns")
        self.btn_send.config(state="disabled")
        
        self.file_frame = tk.Frame(self.main_frame, bg=BG_DARK)
        self.file_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.file_frame.rowconfigure(0, weight=0)
        self.file_frame.rowconfigure(1, weight=1)
        self.file_frame.columnconfigure(0, weight=1)
        
        lbl_file_title = tk.Label(self.file_frame, text="SOLICITAÇÃO DE ARQUIVOS", bg=BG_DARK, fg=ACCENT, font=("Helvetica", 11, "bold"))
        lbl_file_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.file_control_frame = tk.Frame(self.file_frame, bg=BG_LIGHT, padx=15, pady=15, relief="flat", highlightthickness=1, highlightbackground=BG_LIGHT)
        self.file_control_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        
        lbl_req = tk.Label(self.file_control_frame, text="Nome do arquivo no servidor:", bg=BG_LIGHT, fg=FG_LIGHT, font=("Helvetica", 10, "bold"))
        lbl_req.pack(anchor="w", pady=(0, 5))
        
        self.ent_filename = tk.Entry(
            self.file_control_frame, bg=BG_DARK, fg=FG_LIGHT, insertbackground=FG_LIGHT,
            relief="flat", font=("Helvetica", 10), highlightthickness=1,
            highlightbackground=BG_DARK, highlightcolor=ACCENT
        )
        self.ent_filename.pack(fill="x", ipady=5, pady=(0, 10))
        self.ent_filename.config(state="disabled")
        
        self.btn_request = make_button(self.file_control_frame, "Solicitar Download", self.request_file, bg_color=ACCENT_GREEN)
        self.btn_request.pack(fill="x", pady=(0, 20))
        self.btn_request.config(state="disabled")
        
        self.lbl_progress_title = tk.Label(self.file_control_frame, text="Progresso do Download:", bg=BG_LIGHT, fg=FG_LIGHT, font=("Helvetica", 10, "bold"))
        self.lbl_progress_title.pack(anchor="w", pady=(10, 5))
        
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "TProgressbar",
            troughcolor=BG_DARK,
            background=ACCENT_BLUE,
            thickness=15,
            borderwidth=0
        )
        self.progress_bar = ttk.Progressbar(self.file_control_frame, style="TProgressbar", orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)
        
        self.lbl_progress_bytes = tk.Label(self.file_control_frame, text="0 / 0 bytes (0.0%)", bg=BG_LIGHT, fg=FG_SUB, font=("Helvetica", 9))
        self.lbl_progress_bytes.pack(anchor="w", pady=(0, 15))
        
        self.lbl_hash_status = tk.Label(self.file_control_frame, text="Status: Sem downloads ativos", bg=BG_LIGHT, fg=FG_SUB, font=("Helvetica", 10, "bold"))
        self.lbl_hash_status.pack(anchor="w", pady=5)
        
        self.status_bar = tk.Frame(self.root, bg=BG_LIGHT, height=25, padx=10)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        
        self.lbl_system_status = tk.Label(self.status_bar, text="Pronto para conectar.", bg=BG_LIGHT, fg=FG_SUB, font=("Helvetica", 9))
        self.lbl_system_status.pack(side="left")

    def toggle_connection(self):
        if self.client.connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        ip = self.ent_ip.get().strip()
        port_str = self.ent_port.get().strip()
        
        if not ip or not port_str:
            messagebox.showerror("Erro de Validação", "Por favor, preencha o IP e a Porta.")
            return
            
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Erro de Validação", "A porta deve ser um número inteiro válido.")
            return
            
        self.log_system(f"Conectando a {ip}:{port}...")
        self.lbl_status.config(text="● Conectando...", fg=ACCENT)
        self.btn_connect.config(state="disabled")
        
        threading.Thread(target=self._async_connect, args=(ip, port), daemon=True).start()

    def _async_connect(self, ip, port):
        try:
            self.client.connect(ip, port)
            self.root.after(0, self._on_connect_success)
        except Exception as e:
            err_msg = str(e)
            self.root.after(0, self._on_connect_error, err_msg)

    def _on_connect_success(self):
        self.btn_connect.config(state="normal", text="Desconectar", bg=ACCENT_RED, fg=BG_DARK)
        self.lbl_status.config(text="● Conectado", fg=ACCENT_GREEN)
        self.update_connection_state(True)
        self.log_system("Conectado com sucesso ao servidor.")
        
    def _on_connect_error(self, err_msg):
        self.btn_connect.config(state="normal", text="Conectar", bg=ACCENT_BLUE, fg=BG_DARK)
        self.lbl_status.config(text="● Desconectado", fg=ACCENT_RED)
        self.log_system(f"Falha na conexão: {err_msg}")
        
        self.chat_history.config(state="normal")
        self.chat_history.insert("end", "[Erro de Conexão] Não foi possível se conectar ao servidor por timeout ou conexão recusada.\n", "error")
        self.chat_history.config(state="disabled")
        self.chat_history.see("end")
        
        messagebox.showerror("Erro de Conexão", f"Não foi possível se conectar ao servidor:\n{err_msg}")

    def disconnect(self):
        self.client.disconnect()
        self.update_connection_state(False)
        self.log_system("Desconectado do servidor.")

    def update_connection_state(self, is_connected):
        state = "normal" if is_connected else "disabled"
        self.ent_msg.config(state=state)
        self.btn_send.config(state=state)
        self.ent_filename.config(state=state)
        self.btn_request.config(state=state)
        
        conn_state = "disabled" if is_connected else "normal"
        self.ent_ip.config(state=conn_state)
        self.ent_port.config(state=conn_state)
        
        if not is_connected:
            self.btn_connect.config(text="Conectar", bg=ACCENT_BLUE, fg=BG_DARK)
            self.lbl_status.config(text="● Desconectado", fg=ACCENT_RED)

    def send_chat_message(self):
        if not self.client.connected:
            return
            
        msg = self.ent_msg.get().strip()
        if not msg:
            return
            
        try:
            self.client.send_chat(msg)
            
            self.chat_history.config(state="normal")
            self.chat_history.insert("end", "Você: ", "me")
            self.chat_history.insert("end", f"{msg}\n")
            self.chat_history.config(state="disabled")
            self.chat_history.see("end")
            
            self.ent_msg.delete(0, "end")
        except Exception as e:
            self.log_system(f"Erro ao enviar mensagem: {e}")
            self.disconnect()

    def _handle_chat_message(self, msg):
        self.chat_history.config(state="normal")
        
        if msg.startswith("Servidor:"):
            self.chat_history.insert("end", "Servidor: ", "server")
            self.chat_history.insert("end", msg[len("Servidor:"):].strip() + "\n")
        elif msg.startswith("Cliente "):
            partes = msg.split(":", 1)
            self.chat_history.insert("end", partes[0] + ": ", "other")
            if len(partes) > 1:
                self.chat_history.insert("end", partes[1].strip() + "\n")
            else:
                self.chat_history.insert("end", "\n")
        else:
            self.chat_history.insert("end", f"{msg}\n")
            
        self.chat_history.config(state="disabled")
        self.chat_history.see("end")

    def request_file(self):
        if not self.client.connected:
            return
            
        if self.client.download_state['in_progress']:
            messagebox.showwarning("Download em andamento", "Por favor, aguarde a conclusão do download atual.")
            return
            
        nome_arquivo = self.ent_filename.get().strip()
        if not nome_arquivo:
            messagebox.showwarning("Campo vazio", "Insira o nome do arquivo que deseja solicitar.")
            return
            
        try:
            self.progress_bar['value'] = 0
            self.lbl_progress_bytes.config(text="0 / 0 bytes (0.0%)", fg=FG_SUB)
            self.lbl_hash_status.config(text="Status: Enviando solicitação...", fg=ACCENT_BLUE)
            
            self.client.request_file(nome_arquivo)
            self.log_system(f"Solicitado arquivo '{nome_arquivo}' ao servidor.")
        except Exception as e:
            self.log_system(f"Erro ao solicitar arquivo: {e}")
            self.disconnect()

    def _handle_download_start(self, filename, tamanho, sha256):
        self.lbl_hash_status.config(text="Status: Baixando dados...", fg=ACCENT_BLUE)
        self.log_system(f"Iniciando download: '{filename}' ({tamanho} bytes)")
        
        self.progress_bar['maximum'] = tamanho
        self.progress_bar['value'] = 0
        self.lbl_progress_bytes.config(text=f"0 / {tamanho} bytes (0.0%)")

    def _update_download_progress(self, received, total):
        self.progress_bar['value'] = received
        porcentagem = (received / total) * 100 if total > 0 else 0
        self.lbl_progress_bytes.config(text=f"{received} / {total} bytes ({porcentagem:.1f}%)")

    def _handle_download_eof(self, filename, expected_sha256):
        caminho = f"arquivo_recebido_{filename}"
        self.lbl_hash_status.config(text="Status: Verificando integridade (SHA-256)...", fg=ACCENT)
        self.log_system("Transmissão finalizada. Calculando checksum SHA-256...")
        threading.Thread(target=self._async_verify_hash, args=(caminho, expected_sha256, filename), daemon=True).start()

    def _async_verify_hash(self, caminho, expected, filename):
        try:
            hasher = hashlib.sha256()
            with open(caminho, 'rb') as arquivo:
                while True:
                    bloco = arquivo.read(8192)
                    if not bloco:
                        break
                    hasher.update(bloco)
            sha_calculado = hasher.hexdigest()
            self.root.after(0, self._finish_hash_verification, sha_calculado, expected, filename)
        except Exception as e:
            self.root.after(0, self._hash_verification_error, str(e))

    def _finish_hash_verification(self, sha_calculado, expected, filename):
        if sha_calculado == expected:
            self.lbl_hash_status.config(text="Status: HASH OK! Arquivo íntegro.", fg=ACCENT_GREEN)
            self.log_system(f"Sucesso: Checksum do arquivo '{filename}' coincide com o servidor.")
            messagebox.showinfo("Sucesso", f"O arquivo '{filename}' foi baixado e verificado com sucesso!\n\nSHA-256:\n{sha_calculado}")
        else:
            self.lbl_hash_status.config(text="Status: ERRO DE HASH! Arquivo corrompido.", fg=ACCENT_RED)
            self.log_system(f"Erro: Download de '{filename}' corrompido (Hashes divergentes).")
            messagebox.showerror("Erro de Integridade", f"O arquivo '{filename}' está corrompido!\n\nEsperado: {expected}\n\nCalculado: {sha_calculado}")

    def _hash_verification_error(self, err_msg):
        self.lbl_hash_status.config(text="Status: Erro na Verificação", fg=ACCENT_RED)
        self.log_system(f"Erro ao calcular SHA-256: {err_msg}")
        messagebox.showerror("Erro de Verificação", f"Não foi possível calcular o checksum do arquivo:\n{err_msg}")

    def _handle_server_error(self, mensagem):
        self.lbl_hash_status.config(text=f"Erro: {mensagem}", fg=ACCENT_RED)
        self.log_system(f"Servidor retornou erro: {mensagem}")
        
        self.chat_history.config(state="normal")
        self.chat_history.insert("end", "[Erro do Servidor] ", "error")
        self.chat_history.insert("end", f"{mensagem}\n")
        self.chat_history.config(state="disabled")
        self.chat_history.see("end")
        
        messagebox.showerror("Erro do Servidor", mensagem)

    def _handle_connection_lost(self):
        self.log_system("Conexão perdida com o servidor.")
        self.disconnect()
        messagebox.showwarning("Conexão Perdida", "A conexão com o servidor foi encerrada.")

    def log_system(self, msg):
        self.lbl_system_status.config(text=msg)
        self.chat_history.config(state="normal")
        self.chat_history.insert("end", f"[*] {msg}\n", "system")
        self.chat_history.config(state="disabled")
        self.chat_history.see("end")

    def on_closing(self):
        self.disconnect()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
