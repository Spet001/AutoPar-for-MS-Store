import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import shutil
import subprocess
import atexit

BACKUP_SUFFIX = ".bak"
DRY_RUN = False  # Define como False para a operação real

def get_partool_path(log_widget=None):
    partool_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "partool")

    if not os.path.exists(partool_dir):
        log_message(log_widget, f"Pasta 'partool' não encontrada. Criando em: {partool_dir}")
        os.makedirs(partool_dir, exist_ok=True)
        # Se você tiver arquivos do partool embutidos no .exe, eles precisarão ser extraídos aqui.
        # Por exemplo, se eles estiverem no _MEIPASS:
        if getattr(sys, 'frozen', False):
            bundled_dir = os.path.join(sys._MEIPASS, "partool")
            if os.path.exists(bundled_dir):
                shutil.copytree(bundled_dir, partool_dir, dirs_exist_ok=True)
            else:
                log_message(log_widget, "Aviso: Pasta 'partool' não encontrada no executável empacotado.")
        else:
            log_message(log_widget, "Aviso: Executando em modo de script. A pasta 'partool' precisa estar no diretório do script.")
            # A linha abaixo pode ser necessária se a pasta já existe mas está faltando arquivos
            # shutil.copytree("partool_source_dir", partool_dir, dirs_exist_ok=True)

    partool_dll_path = os.path.join(partool_dir, "ParTool.dll")
    if not os.path.exists(partool_dll_path):
        raise FileNotFoundError(f"Erro: O arquivo 'ParTool.dll' não foi encontrado em {partool_dir}.")
    
    return partool_dll_path

# As outras funções (log_message, safe_copy, do_repack) permanecem as mesmas.
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
    try:
        PARTOOL_PATH = get_partool_path(log_widget)
    except FileNotFoundError as e:
        log_message(log_widget, str(e))
        return

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
    
# A função de limpeza de diretório temporário não é mais necessária, pois não usamos mais um diretório temporário global para o partool.
# atexit.register(cleanup_temp_dir)

def start_gui():
    window = tk.Tk()
    window.title("AutoPAR Repacker")
    window.geometry("800x600")

    main_frame = tk.Frame(window, padx=10, pady=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame para as entradas
    input_frame = tk.LabelFrame(main_frame, text="Configurações", padx=10, pady=10)
    input_frame.pack(fill=tk.X)

    tk.Label(input_frame, text="MOD Folder:", anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
    mod_entry = tk.Entry(input_frame)
    mod_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(input_frame, text="Procurar", command=lambda: mod_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(input_frame, text="Game Folder:", anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="ew")
    game_entry = tk.Entry(input_frame)
    game_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(input_frame, text="Procurar", command=lambda: game_entry.insert(0, filedialog.askdirectory())).grid(row=1, column=2, padx=5, pady=5)
    
    input_frame.grid_columnconfigure(1, weight=1)

    # Botão de Iniciar
    button_frame = tk.Frame(main_frame, pady=10)
    button_frame.pack(fill=tk.X)
    
    def on_start():
        mod_path = mod_entry.get()
        game_path = game_entry.get()
        if not mod_path or not game_path:
            messagebox.showerror("Erro", "Por favor, selecione as pastas do MOD e do Jogo.")
            return
        log_output.delete("1.0", tk.END)
        threading.Thread(target=do_repack, args=(mod_path, game_path, log_output), daemon=True).start()

    tk.Button(button_frame, text="Start Repack", command=on_start).pack(fill=tk.X)
    
    # Área de Log
    log_frame = tk.LabelFrame(main_frame, text="Log", padx=5, pady=5)
    log_frame.pack(fill=tk.BOTH, expand=True)
    log_output = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
    log_output.pack(fill=tk.BOTH, expand=True)

    window.mainloop()

if __name__ == "__main__":
    start_gui()