import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import threading
import os
import json
import tempfile

# Variáveis globais para controle do processamento
processamento_ativo = False
cancelar_processamento = False
status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')

# Função para centralizar a janela na tela
def centralizar_janela(janela, largura, altura):
    # Obtém as dimensões da tela
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    # Calcula a posição x e y para centralizar a janela
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    # Define a geometria da janela
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# Função para abrir a pasta de imagens processadas
def abrir_pasta_processada():
    # Supondo que as imagens processadas estejam na pasta "output"
    pasta_processada = "Output"
    if os.path.exists(pasta_processada):
        # Abre a pasta no explorador de arquivos
        if os.name == "nt":
            os.startfile(pasta_processada)
        elif os.name == "posix":
            subprocess.run(["open", pasta_processada] if os.name == "posix" else ["xdg-open", pasta_processada])
    else:
        status_label.config(text="Pasta de processamento não encontrada!")

# Função para processar os arquivos em uma thread separada
def atualizar_status_processamento(status):
    try:
        with open(status_file, 'w') as f:
            json.dump(status, f)
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")

def processar_arquivos(file_paths):
    global processamento_ativo, cancelar_processamento
    import time
    
    processamento_ativo = True
    cancelar_processamento = False
    
    # Mostra a barra de progresso e o status
    progress_bar.pack(pady=10)
    status_label.pack(pady=10)
    status_label.config(text="Processando...")
    tempo_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0")
    tempo_label.pack(pady=5)
    btn_cancelar.pack(pady=5) 
    progress_bar["value"] = 0
    root.update_idletasks()

    # Processa cada arquivo
    total_files = len(file_paths)
    start_time = time.time()
    tempos_processamento = []

    # Cria pasta Output se não existir
    if not os.path.exists('Output'):
        os.makedirs('Output')

    for i, file_path in enumerate(file_paths):
        if cancelar_processamento:
            break
            
        arquivo_start_time = time.time()
        
        # Atualiza status para o processo filho
        atualizar_status_processamento({
            'deve_continuar': True,
            'arquivo_atual': file_path
        })
        
        try:
            processo = subprocess.Popen(["python", "processamento.py", file_path],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            
            while processo.poll() is None:
                if cancelar_processamento:
                    atualizar_status_processamento({'deve_continuar': False})
                    processo.terminate()
                    break
                root.update()
                time.sleep(0.1)
            
            if not cancelar_processamento:
                stdout, stderr = processo.communicate()
                if processo.returncode != 0:
                    try:
                        erro_msg = stderr.decode('utf-8')
                    except UnicodeDecodeError:
                        erro_msg = stderr.decode('latin-1')
                    messagebox.showerror("Erro", f"Erro ao processar {os.path.basename(file_path)}:\n{erro_msg}")
                    continue
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao executar processamento: {str(e)}")
            continue
            
        tempo_arquivo = time.time() - arquivo_start_time
        tempos_processamento.append(tempo_arquivo)
        
        # Calcula tempo médio e estimativa restante
        tempo_medio = sum(tempos_processamento) / len(tempos_processamento)
        arquivos_restantes = total_files - (i + 1)
        tempo_restante = int(tempo_medio * arquivos_restantes)
        
        progress_bar["value"] = (i + 1) / total_files * 100
        tempo_label.config(text=f"Processando {i + 1}/{total_files} arquivos - Tempo restante: {tempo_restante} segundos")
        root.update_idletasks()

    # Limpa o arquivo de status
    if os.path.exists(status_file):
        try:
            os.remove(status_file)
        except:
            pass

    # Oculta a barra de progresso após o processamento
    progress_bar.pack_forget()
    tempo_label.pack_forget()
    btn_cancelar.pack_forget()
    processamento_ativo = False

    # Atualiza o status após o processamento
    if cancelar_processamento:
        status_label.config(text="Processamento cancelado!")
        cancelar_processamento = False
    else:
        status_label.config(text="Processamento concluído!")
        # Exibe o botão para abrir a pasta de processamento
        btn_abrir_pasta.pack(pady=10)

# Função para cancelar o processamento
def cancelar_processo():
    global cancelar_processamento
    if processamento_ativo:
        if messagebox.askyesno("Cancelar", "Deseja realmente cancelar o processamento?"):
            cancelar_processamento = True
            status_label.config(text="Cancelando...")

# Função para selecionar arquivos
def selecionar_arquivo():
    # Oculta o botão de abrir pasta e a mensagem de conclusão anterior
    btn_abrir_pasta.pack_forget()
    status_label.config(text="")

    # Permite selecionar múltiplos arquivos
    file_paths = filedialog.askopenfilenames(
        title="Selecione uma ou mais imagens/vídeos",
        filetypes=[("Imagens", "*.jpg;*.jpeg;*.png"), ("Vídeos", "*.mp4;*.avi")]
    )
    if file_paths:
        # Inicia o processamento em uma thread separada
        threading.Thread(target=processar_arquivos, args=(file_paths,)).start()

# Função para desenhar um retângulo com bordas arredondadas
def criar_retangulo_arredondado(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
        x1 + radius, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)

# Função para criar um botão com bordas arredondadas
def criar_botao_arredondado(parent, text, command, bg_color, fg_color, width=200, height=40, corner_radius=20):
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg_color, highlightthickness=0)
    canvas.pack(pady=20)

    # Desenha um retângulo com bordas arredondadas
    criar_retangulo_arredondado(canvas, 0, 0, width, height, radius=corner_radius, fill=bg_color, outline=bg_color)

    # Adiciona o texto no centro do botão
    canvas.create_text(width/2, height/2, text=text, font=("Helvetica", 12), fill=fg_color)

    # Adiciona um evento de clique ao botão
    canvas.bind("<Button-1>", lambda event: command())

    return canvas

# Criando a interface gráfica
root = tk.Tk()
root.title("RePosture")
root.geometry("600x400")  # Tamanho da janela
root.configure(bg="#f0f0f0")  # Fundo cinza claro

# Centraliza a janela na tela
centralizar_janela(root, 600, 400)

# Título personalizado
titulo = tk.Label(
    root,
    text="RePosture",
    font=("Helvetica", 24, "bold"),
    fg="#000080",  # Cor do texto (azul escuro)
    bg="#f0f0f0"   # Cor de fundo do título (cinza claro)
)
titulo.pack(pady=20)

# Adiciona o botão personalizado para selecionar arquivos
btn_selecionar = criar_botao_arredondado(
    root,
    text="Selecionar Arquivos",
    command=selecionar_arquivo,
    bg_color="#000080",  # Cor de fundo do botão (azul escuro)
    fg_color="white",  # Cor do texto (branco)
    width=200,
    height=40,
    corner_radius=20
)

# Barra de progresso (inicialmente oculta)
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")

# Label para exibir o status do processamento (inicialmente oculto)
status_label = tk.Label(root, text="", font=("Helvetica", 12), bg="#f0f0f0")

# Botão para abrir a pasta de processamento (inicialmente oculto)
btn_abrir_pasta = criar_botao_arredondado(
    root,
    text="Imagens Processadas",
    command=abrir_pasta_processada,
    bg_color="#fde910",  # Cor de fundo do botão (amarelo)
    fg_color="black",  # Cor do texto (preto)
    width=250,
    height=40,
    corner_radius=20
)
btn_abrir_pasta.pack_forget()  # Oculta o botão inicialmente

# Botão para cancelar processamento (inicialmente oculto)
btn_cancelar = criar_botao_arredondado(
    root,
    text="Cancelar Processamento",
    command=cancelar_processo,
    bg_color="#ff0000",  # Vermelho para indicar ação de cancelamento
    fg_color="white",
    width=200,
    height=40,
    corner_radius=20
)
btn_cancelar.pack_forget()  # Oculta o botão inicialmente

# Inicia o loop da interface
root.mainloop()