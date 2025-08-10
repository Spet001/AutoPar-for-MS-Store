import os
import sys
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import shutil
import subprocess
import atexit

BACKUP_SUFFIX = ".bak"
DRY_RUN = False  # Define como False para a operação real

_TEMP_DIR = None

def get_partool_path(log_widget=None):
    global _TEMP_DIR
    _TEMP_DIR = tempfile.mkdtemp()
    temp_partool_dir = os.path.join(_TEMP_DIR, "partool")
    os.makedirs(temp_partool_dir, exist_ok=True)

    try:
        if getattr(sys, 'frozen', False):
            bundled_dir = os.path.join(sys._MEIPASS, "partool")
            shutil.copytree(bundled_dir, temp_partool_dir, dirs_exist_ok=True)
        else:
            shutil.copytree("partool", temp_partool_dir, dirs_exist_ok=True)
    except Exception as e:
        raise FileNotFoundError(f"Erro ao localizar ou extrair a pasta 'partool': {e}")

    # Log extra para debug
    if log_widget:
        log_message(log_widget, f"[DEBUG] Pasta temporária criada: {_TEMP_DIR}")
        for root, dirs, files in os.walk(temp_partool_dir):
            for file in files:
                log_message(log_widget, f"[DEBUG] Arquivo extraído: {os.path.relpath(os.path.join(root, file), temp_partool_dir)}")

    return os.path.join(temp_partool_dir, "ParTool.dll")

def cleanup_temp_dir():
    global _TEMP_DIR
    if _TEMP_DIR and os.path.exists(_TEMP_DIR):
        try:
            shutil.rmtree(_TEMP_DIR)
        except Exception:
            pass

atexit.register(cleanup_temp_dir)

def log_message(log_widget, message):
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)

def safe_copy(src_file, dst_file, log_widget):
    if os.path.exists(dst_file):
        if not os.path.exists(dst_file + BACKUP_SUFFIX):
            try:
                shutil.copy2(dst_file, dst_file + BACKUP_SUFFIX)
                log_message(log_widget, f"Criado backup: {dst_file + BACKUP_SUFFIX}")
            except Exception as e:
                log_message(log_widget, f"ERRO ao criar backup de {dst_file}: {e}")
    
    try:
        if not DRY_RUN:
            shutil.copy2(src_file, dst_file)
            log_message(log_widget, f"Copiado: {dst_file}")
    except Exception as e:
        log_message(log_widget, f"ERRO ao copiar {src_file} para {dst_file}: {e}")

def do_repack(mod_folder, game_folder, log_widget):
    log_message(log_widget, "Iniciando o processo de repack...")
    PARTOOL_PATH = get_partool_path(log_widget)

    par_files_to_add = {}
    temp_mod_base_dir = os.path.join(game_folder, "temp_mod_par")
    
    try:
        for root, dirs, files in os.walk(mod_folder):
            for file in files:
                mod_file_path = os.path.join(root, file)
                relative_path = os.path.relpath(mod_file_path, mod_folder)
                parts = relative_path.split(os.sep)

                if len(parts) < 2:
                    game_dst_path = os.path.join(game_folder, *parts)
                    os.makedirs(os.path.dirname(game_dst_path), exist_ok=True)
                    log_message(log_widget, f"Copiando para pasta descompactada: {relative_path}")
                    safe_copy(mod_file_path, game_dst_path, log_widget)
                else:
                    par_name = parts[0]
                    game_par_path = os.path.join(game_folder, par_name + ".par")

                    if os.path.exists(game_par_path):
                        if par_name not in par_files_to_add:
                            par_files_to_add[par_name] = []
                        par_files_to_add[par_name].append(mod_file_path)
                    else:
                        game_dst_path = os.path.join(game_folder, *parts)
                        os.makedirs(os.path.dirname(game_dst_path), exist_ok=True)
                        log_message(log_widget, f"Copiando para pasta descompactada: {relative_path}")
                        safe_copy(mod_file_path, game_dst_path, log_widget)

        for par_name, files_to_add in par_files_to_add.items():
            original_par_path = os.path.join(game_folder, par_name + ".par")
            temp_par_path = os.path.join(game_folder, par_name + ".temp.par")
            
            temp_mod_dir = os.path.join(temp_mod_base_dir, par_name)
            os.makedirs(temp_mod_dir, exist_ok=True)
            
            for mod_file_path in files_to_add:
                relative_path_in_mod = os.path.relpath(mod_file_path, os.path.join(mod_folder, par_name))
                temp_file_path = os.path.join(temp_mod_dir, relative_path_in_mod)
                os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
                safe_copy(mod_file_path, temp_file_path, log_widget)

            if os.path.exists(original_par_path) and not os.path.exists(original_par_path + BACKUP_SUFFIX):
                log_message(log_widget, f"Criando backup do .par original: {original_par_path}")
                shutil.copy2(original_par_path, original_par_path + BACKUP_SUFFIX)
            
            log_message(log_widget, f"Adicionando arquivos de mod para {par_name}.par...")
            if not DRY_RUN:
                try:
                    cmd = [
                        "dotnet", PARTOOL_PATH, "add",
                        original_par_path, temp_mod_dir, temp_par_path, "-c", "0"
                    ]
                    log_message(log_widget, f"[DEBUG] Comando executado: {' '.join(cmd)}")

                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    
                    log_message(log_widget, f"ParTool stdout: {result.stdout.strip()}")
                    if result.stderr:
                        log_message(log_widget, f"ParTool stderr: {result.stderr.strip()}")

                    if os.path.exists(temp_par_path):
                        log_message(log_widget, f"Substituindo {original_par_path} com o novo .par...")
                        shutil.move(temp_par_path, original_par_path)
                        log_message(log_widget, f"Atualizado com sucesso: {original_par_path}")
                    else:
                        log_message(log_widget, f"ERRO: {temp_par_path} não foi criado. Falha no ParTool?")

                except FileNotFoundError:
                    log_message(log_widget, "ERRO: O executável 'dotnet' ou a ferramenta ParTool não foram encontrados.")
                except subprocess.CalledProcessError as e:
                    log_message(log_widget, f"ERRO ao adicionar arquivos a {par_name}.par: O comando falhou com código de retorno {e.returncode}.")
                    log_message(log_widget, f"Detalhes do erro:\n{e.stderr.strip()}")

    except Exception as e:
        log_message(log_widget, f"Um erro inesperado ocorreu: {e}")
    finally:
        if os.path.exists(temp_mod_base_dir):
            shutil.rmtree(temp_mod_base_dir)
            log_message(log_widget, f"Diretórios temporários limpos.")
        log_message(log_widget, "Processo de repack concluído!")
    
def start_gui():
    window = tk.Tk()
    window.title("PAR Repacker (DEBUG)")

    tk.Label(window, text="Selecione a Pasta do MOD").grid(row=0, column=0, padx=5, pady=5)
    mod_entry = tk.Entry(window, width=60)
    mod_entry.grid(row=0, column=1)
    tk.Button(window, text="Procurar", command=lambda: mod_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2)

    tk.Label(window, text="Selecione a Pasta do Jogo").grid(row=1, column=0, padx=5, pady=5)
    game_entry = tk.Entry(window, width=60)
    game_entry.grid(row=1, column=1)
    tk.Button(window, text="Procurar", command=lambda: game_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2)

    log_output = scrolledtext.ScrolledText(window, width=100, height=30)
    log_output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def on_start():
        mod_path = mod_entry.get()
        game_path = game_entry.get()
        if not mod_path or not game_path:
            messagebox.showerror("Erro", "Por favor, selecione as pastas do MOD e do Jogo.")
            return
        log_output.delete("1.0", tk.END)
        threading.Thread(target=do_repack, args=(mod_path, game_path, log_output), daemon=True).start()

    tk.Button(window, text="Iniciar", command=on_start).grid(row=2, column=1, pady=10)

    window.mainloop()

if __name__ == "__main__":
    start_gui()
