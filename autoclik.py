import subprocess
import sys
import importlib
import os
import threading
import time
import shutil

def install_and_import(package):
    try:
        importlib.import_module(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if not getattr(sys, 'frozen', False):
    install_and_import('customtkinter')
    install_and_import('pyautogui')
    install_and_import('keyboard')
    install_and_import('pyinstaller')

import customtkinter as ctk
import pyautogui as auto
import keyboard

ctk.set_appearance_mode("dark")

class AutoPython(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AutoPython")
        self.geometry("400x500")
        self.attributes("-topmost", True)

        self.running = False
        self.mouse_pos = (0, 0)
        auto.FAILSAFE = True 

        self.label_titulo = ctk.CTkLabel(self, text="AutoPython", font=("Roboto", 26, "bold"), text_color="#1f538d")
        self.label_titulo.pack(pady=20)

        self.pos_label = ctk.CTkLabel(self, text="Posição: X=0, Y=0")
        self.pos_label.pack(pady=5)

        self.btn_capturar = ctk.CTkButton(self, text="Capturar Posição (5s)", command=self.start_capture_thread)
        self.btn_capturar.pack(pady=10)

        self.delay_entry = ctk.CTkEntry(self, placeholder_text="Intervalo (ex: 0.1)")
        self.delay_entry.insert(0, "0.1")
        self.delay_entry.pack(pady=10)

        self.btn_main = ctk.CTkButton(self, text="INICIAR (F8)", fg_color="green", command=self.toggle_clicker)
        self.btn_main.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="Status: Parado | Atalho: F8", text_color="gray")
        self.status_label.pack(pady=5)

        if not getattr(sys, 'frozen', False):
            self.sep = ctk.CTkLabel(self, text="_______________________________________", text_color="gray30")
            self.sep.pack(pady=10)
            self.btn_install = ctk.CTkButton(self, text="GERAR APLICATIVO (.EXE)", fg_color="#333333", command=self.start_install_thread)
            self.btn_install.pack(pady=30)

        keyboard.add_hotkey('f8', self.toggle_clicker)

    def start_capture_thread(self):
        self.btn_capturar.configure(state="disabled")
        threading.Thread(target=self.capture_position, daemon=True).start()

    def capture_position(self):
        for i in range(5, 0, -1):
            self.btn_capturar.configure(text=f"Mova o mouse... {i}s")
            time.sleep(1)
        self.mouse_pos = auto.position()
        self.pos_label.configure(text=f"Posição: X={self.mouse_pos[0]}, Y={self.mouse_pos[1]}")
        self.btn_capturar.configure(state="normal", text="Capturar Posição (5s)")

    def toggle_clicker(self):
        if not self.running:
            self.running = True
            self.btn_main.configure(text="PARAR (F8)", fg_color="red")
            self.status_label.configure(text="Status: RODANDO", text_color="green")
            try:
                delay = float(self.delay_entry.get().replace(',', '.'))
            except ValueError:
                delay = 0.1
            threading.Thread(target=self.click_loop, args=(delay,), daemon=True).start()
        else:
            self.running = False
            self.btn_main.configure(text="INICIAR (F8)", fg_color="green")
            self.status_label.configure(text="Status: Parado", text_color="gray")

    def click_loop(self, delay):
        while self.running:
            auto.click(self.mouse_pos[0], self.mouse_pos[1])
            time.sleep(delay)

    def start_install_thread(self):
        self.btn_install.configure(state="disabled", text="Gerando... Aguarde")
        threading.Thread(target=self.make_exe, daemon=True).start()

    def make_exe(self):
        script_path = os.path.abspath(sys.argv[0])
        exe_name = "AutoPython"
        try:
            # CHAMADA CORRIGIDA: Usa o sys.executable para chamar o PyInstaller como módulo
            subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "--noconsole",
                "--onefile",
                "--clean",
                "--collect-all", "customtkinter",
                "--name", exe_name,
                script_path
            ], check=True)

            if os.path.exists("build"): shutil.rmtree("build")
            if os.path.exists(f"{exe_name}.spec"): os.remove(f"{exe_name}.spec")

            self.btn_install.configure(text="SUCESSO! (Pasta dist)", fg_color="green")
            os.startfile("dist")
        except Exception as e:
            self.btn_install.configure(text="Erro ao gerar EXE", fg_color="red", state="normal")
            print(f"Erro detalhado: {e}")

if __name__ == "__main__":
    app = AutoPython()
    app.mainloop()