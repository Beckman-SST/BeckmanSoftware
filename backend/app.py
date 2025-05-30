import os
import sys
import time
import threading
import subprocess
import json
import tempfile
import glob
import re
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from video_processor import process_video_file as process_video

# Função para processar vídeo (wrapper para manter compatibilidade)
def process_video_file(input_path):
    try:
        success, result = process_video(input_path, app.config['OUTPUT_FOLDER'])
        if success:
            return True, f"Vídeo processado com sucesso: {result}"
        return False, result
    except Exception as e:
        return False, f"Erro durante o processamento do vídeo: {str(e)}"

# Configurações da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'beckman_project_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules', 'data', 'uploads'))
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules', 'data', 'output'))
app.config['MERGE_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules', 'data', 'merge'))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'mp4', 'avi'}
app.config['CONFIG_FILE'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json'))
app.config['IMAGES_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules', 'data', 'images'))
app.config['VIDEOS_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'modules', 'data', 'videos'))

# Garante que as pastas necessárias existem
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['MERGE_FOLDER'], app.config['IMAGES_FOLDER'], app.config['VIDEOS_FOLDER']]:
    try:
        os.makedirs(folder, exist_ok=True)
        print(f"Pasta criada/verificada com sucesso: {folder}")
    except Exception as e:
        print(f"Erro ao criar/verificar pasta {folder}: {e}")

# Variáveis globais para controle do processamento
processamento_ativo = False
cancelar_processamento = False
status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
arquivo_atual = 0
total_files = 0
tempos_processamento = []
processing_logs = []  # Lista para armazenar os logs do processamento

# Função para adicionar log
def add_log(message):
    global processing_logs
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    log_entry = f'[{timestamp}] {message}'
    processing_logs.append(log_entry)
    # Manter apenas os últimos 100 logs
    if len(processing_logs) > 100:
        processing_logs = processing_logs[-100:]

# Configurações padrão
default_config = {
    'min_detection_confidence': 0.80,
    'min_tracking_confidence': 0.80,
    'yolo_confidence': 0.65,
    'moving_average_window': 5,
    'show_face_blur': True,
    'show_electronics': True,
    'show_angles': True,
    'show_upper_body': True,
    'show_lower_body': True,
    'process_lower_body': True,
    'resize_width': 800
}

# Carrega as configurações do arquivo ou usa as padrões
def load_config():
    try:
        if os.path.exists(app.config['CONFIG_FILE']):
            with open(app.config['CONFIG_FILE'], 'r') as f:
                return json.load(f)
        return default_config.copy()
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return default_config.copy()

# Salva as configurações no arquivo
def save_config_to_file(config):
    try:
        with open(app.config['CONFIG_FILE'], 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# Verifica se as pastas necessárias existem
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['IMAGES_FOLDER'], app.config['VIDEOS_FOLDER']]:
    try:
        os.makedirs(folder, exist_ok=True)
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
    except Exception as e:
        print(f"Erro ao criar/verificar pasta {folder}: {e}")

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Função para atualizar o status do processamento
def atualizar_status_processamento(status):
    try:
        # Adiciona as configurações atuais ao status
        status['config'] = load_config()
        with open(status_file, 'w') as f:
            json.dump(status, f)
    except Exception as e:
        print(f"Erro ao atualizar status: {e}")

# Função para extrair erros dos logs
def extract_errors_from_log(log_file):
    try:
        # Tenta ler com UTF-8 primeiro, depois fallback para latin-1
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(log_file, 'r', encoding='latin-1') as f:
                content = f.read()
            
        # Procura por mensagens de erro no log
        error_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ERROR - (.+)'
        errors = re.findall(error_pattern, content)
        return errors
    except Exception as e:
        print(f"Erro ao extrair erros do log: {e}")
        return []

# Função para processar os arquivos em uma thread separada
# Lista thread-safe para armazenar mensagens de erro
error_messages = []

def adicionar_erro(mensagem):
    """Adiciona uma mensagem de erro à lista thread-safe"""
    error_messages.append(mensagem)

def processar_arquivos(file_paths):
    global processamento_ativo, cancelar_processamento, arquivo_atual, total_files, tempos_processamento
    
    processamento_ativo = True
    cancelar_processamento = False
    error_messages.clear()  # Limpa mensagens de erro anteriores
    processing_logs.clear()  # Limpa logs anteriores
    
    add_log('Iniciando processamento de arquivos')
    
    # Limpa o arquivo de status
    status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
    if os.path.exists(status_file):
        try:
            with open(status_file, 'w') as f:
                json.dump({'deve_continuar': True}, f)
        except Exception as e:
            print(f"Erro ao limpar arquivo de status: {e}")
    
    # Processa cada arquivo
    total_files = len(file_paths)
    tempos_processamento = []
    arquivo_atual = 0
    tempo_inicio = time.time()
    
    add_log(f'Total de arquivos para processar: {total_files}')

    for i, file_path in enumerate(file_paths):
        if cancelar_processamento:
            add_log('Processamento cancelado pelo usuário')
            break
            
        arquivo_atual = i + 1
        arquivo_start_time = time.time()
        filename = os.path.basename(file_path)
        log_messages = []  # Lista para agrupar mensagens de log do arquivo atual
        
        # Atualiza status
        atualizar_status_processamento({
            'deve_continuar': True,
            'arquivo_atual': file_path
        })
        
        try:
            # Verifica se é um arquivo de vídeo
            if file_path.lower().endswith(('.mp4', '.avi')):
                log_messages.append(f'Iniciando processamento do vídeo')
                success, message = process_video_file(file_path)
                if not success:
                    log_messages.append(f'Erro no processamento: {message}')
                    adicionar_erro(message)
                    continue
                log_messages.append('Vídeo processado com sucesso')
            else:
                # Processamento de imagens usando o módulo modular
                log_messages.append('Iniciando processamento da imagem')
                output_folder = app.config['OUTPUT_FOLDER']
                processo = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "modules", "processamento.py"), file_path, "-o", output_folder],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
                
                while processo.poll() is None:
                    if cancelar_processamento:
                        processo.terminate()
                        log_messages.append('Processamento interrompido')
                        break
                    time.sleep(0.1)
                
                if not cancelar_processamento:
                    stdout, stderr = processo.communicate()
                    
                    # Verifica o código de retorno do processo
                    if processo.returncode != 0:
                        erro = stderr.decode('utf-8', errors='ignore')
                        log_messages.append(f'Erro no processamento: {erro}')
                        adicionar_erro(f"Erro ao processar {filename}: {erro}")
                    else:
                        log_messages.append('Processamento concluído com sucesso')
            
            # Remove o arquivo de upload após processamento
            try:
                os.remove(file_path)
            except Exception as e:
                log_messages.append(f'Erro ao remover arquivo de upload: {str(e)}')
                print(f"Erro ao remover arquivo {file_path}: {e}")
            
            # Calcula tempo de processamento
            tempo_processamento = time.time() - arquivo_start_time
            tempos_processamento.append(tempo_processamento)
            log_messages.append(f'Tempo de processamento: {int(tempo_processamento)} segundos')
                
        except Exception as e:
            log_messages.append(f'Erro inesperado: {str(e)}')
            adicionar_erro(f"Erro inesperado ao processar {filename}: {str(e)}")
        
        # Adiciona todas as mensagens do arquivo atual como um único log
        add_log(f'Arquivo {arquivo_atual}/{total_files} - {filename}:\n' + '\n'.join(f'  - {msg}' for msg in log_messages))
    
    tempo_total = time.time() - tempo_inicio
    add_log(f'Processamento finalizado. Tempo total: {int(tempo_total)} segundos')
    
    processamento_ativo = False
    cancelar_processamento = False
    return True

# Rota principal
@app.route('/get_errors')
def get_errors():
    """Endpoint para recuperar mensagens de erro acumuladas"""
    global error_messages
    return jsonify(errors=error_messages)

@app.route('/')
def index():
    # Lista os arquivos processados
    processed_files = []
    error_files = []
    
    # Exibe erros acumulados, se houver
    for error in error_messages:
        flash(error, 'error')
    error_messages.clear()
    
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        # Filtra apenas arquivos de imagem e vídeo, excluindo arquivos como __init__.py
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.mp4', '.avi', '.mov', '.mkv')
        all_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) 
                    if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f)) 
                    and f.lower().endswith(valid_extensions)]
        
        # Separa os arquivos de erro dos arquivos processados normalmente
        for f in all_files:
            if f.startswith('error_'):
                error_files.append(f)
            else:
                processed_files.append(f)
    
    return render_template('index.html', processed_files=processed_files, error_files=error_files)

# Rota para a página de configurações
@app.route('/config')
def config():
    # Carrega as configurações atuais
    current_config = load_config()
    return render_template('config.html', config=current_config)

# Rota para salvar configurações
@app.route('/save_config', methods=['POST'])
def save_config():
    # Obtém as configurações do formulário
    new_config = {
        'min_detection_confidence': float(request.form.get('min_detection_confidence', default_config['min_detection_confidence'])),
        'min_tracking_confidence': float(request.form.get('min_tracking_confidence', default_config['min_tracking_confidence'])),
        'yolo_confidence': float(request.form.get('yolo_confidence', default_config['yolo_confidence'])),
        'moving_average_window': int(request.form.get('moving_average_window', default_config['moving_average_window'])),
        'show_face_blur': 'show_face_blur' in request.form,
        'show_electronics': 'show_electronics' in request.form,
        'show_angles': 'show_angles' in request.form,
        'show_upper_body': 'show_upper_body' in request.form,
        'show_lower_body': 'show_lower_body' in request.form,
        'process_lower_body': 'process_lower_body' in request.form,
        'resize_width': int(request.form.get('resize_width', default_config['resize_width']))
    }
    
    # Salva as configurações
    if save_config_to_file(new_config):
        flash('Configurações salvas com sucesso!', 'success')
    else:
        flash('Erro ao salvar configurações.', 'error')
    
    return redirect(url_for('config'))

# Rota para upload de arquivos
@app.route('/upload', methods=['POST'])
def upload_file():
    global processamento_ativo
    
    if processamento_ativo:
        flash('Já existe um processamento em andamento. Aguarde a conclusão.', 'warning')
        return redirect(url_for('index'))
    
    # Verifica se há arquivos no request
    if 'files' not in request.files:
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    
    # Verifica se algum arquivo foi selecionado
    if not files or files[0].filename == '':
        flash('Nenhum arquivo selecionado', 'error')
        return redirect(url_for('index'))
    
    # Lista para armazenar os caminhos dos arquivos válidos
    valid_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(file_path)
                valid_files.append(file_path)
            except Exception as e:
                print(f"Erro ao salvar arquivo {filename}: {e}")
                flash(f'Erro ao salvar arquivo {filename}: {e}', 'error')
        else:
            flash(f'Arquivo {file.filename} não permitido. Use apenas imagens (jpg, jpeg, png) ou vídeos (mp4, avi).', 'error')
    
    if valid_files:
        # Inicia o processamento em uma thread separada
        threading.Thread(target=processar_arquivos, args=(valid_files,)).start()
        flash(f'{len(valid_files)} arquivo(s) enviado(s) para processamento', 'success')
    
    return redirect(url_for('index'))

# Rota para cancelar o processamento
@app.route('/cancelar', methods=['POST'])
def cancelar():
    global cancelar_processamento
    
    if processamento_ativo:
        cancelar_processamento = True
        flash('Solicitação de cancelamento enviada. Aguarde...', 'info')
    else:
        flash('Não há processamento ativo para cancelar', 'warning')
    
    return redirect(url_for('index'))

# Rota para verificar o status do processamento
@app.route('/status')
def status():
    global arquivo_atual, total_files, tempos_processamento, error_messages, processing_logs
    
    status_info = {
        'ativo': processamento_ativo,
        'cancelando': cancelar_processamento,
        'erros': error_messages[:],  # Envia uma cópia da lista de erros
        'arquivos_processados': [],
        'logs': processing_logs[:]  # Adiciona os logs ao retorno
    }
    
    # Verifica arquivos já processados na pasta Output
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        # Filtra apenas arquivos de imagem e vídeo
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.mp4', '.avi', '.mov', '.mkv')
        status_info['arquivos_processados'] = [
            f for f in os.listdir(app.config['OUTPUT_FOLDER'])
            if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f))
            and f.lower().endswith(valid_extensions)
        ]
    
    if processamento_ativo and arquivo_atual > 0:
        # Calcula tempo médio e estimativa restante
        tempo_medio = sum(tempos_processamento) / len(tempos_processamento) if tempos_processamento else 0
        arquivos_restantes = total_files - arquivo_atual
        tempo_restante = int(tempo_medio * arquivos_restantes) if tempo_medio > 0 else 0
        
        # Adiciona informações detalhadas de progresso
        status_info.update({
            'arquivo_atual': arquivo_atual,
            'total_arquivos': total_files,
            'progresso': (arquivo_atual / total_files) * 100 if total_files > 0 else 0,
            'tempo_restante': tempo_restante,
            'tempo_medio_por_arquivo': round(tempo_medio, 2) if tempo_medio > 0 else 0
        })
    
    return jsonify(status_info)

# Rota para servir os arquivos processados
@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Rota para limpar os arquivos processados
@app.route('/limpar', methods=['POST'])
def limpar():
    if processamento_ativo:
        flash('Não é possível limpar enquanto há um processamento em andamento', 'warning')
        return redirect(url_for('index'))
    
    # Limpa a pasta de uploads
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Erro ao remover arquivo temporário {file_path}: {e}")
                flash(f'Erro ao remover arquivo temporário {filename}: {e}', 'error')
    
    flash('Arquivos temporários removidos com sucesso', 'success')
    return redirect(url_for('index'))

# Rota para abrir a pasta de output
@app.route('/abrir-pasta')
def abrir_pasta():
    output_path = os.path.abspath(app.config['OUTPUT_FOLDER'])
    if os.path.exists(output_path):
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':  # macOS e Linux
            subprocess.Popen(['open', output_path] if sys.platform == 'darwin' else ['xdg-open', output_path])
    return {'success': True, 'path': output_path}

# Rota para abrir a pasta de merge
@app.route('/abrir-pasta-merge')
def abrir_pasta_merge():
    merge_path = os.path.abspath(app.config['MERGE_FOLDER'])
    if os.path.exists(merge_path):
        if os.name == 'nt':  # Windows
            os.startfile(merge_path)
        elif os.name == 'posix':  # macOS e Linux
            subprocess.Popen(['open', merge_path] if sys.platform == 'darwin' else ['xdg-open', merge_path])
    return {'success': True, 'path': merge_path}

# Rota para a página de relatório
@app.route('/relatorio')
def relatorio():
    processed_files = []
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        # Filtra apenas arquivos de imagem e vídeo, excluindo arquivos de erro
        valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.mp4', '.avi', '.mov', '.mkv')
        processed_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) 
                        if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f)) 
                        and not f.startswith('error_')
                        and f.lower().endswith(valid_extensions)]
    return render_template('relatorio.html', processed_files=processed_files)

# Rota para unir imagens selecionadas
# Rota para servir arquivos da pasta Merge
@app.route('/merge/<filename>')
def merge_file(filename):
    return send_from_directory(app.config['MERGE_FOLDER'], filename)

@app.route('/unir_imagens', methods=['POST'])
def unir_imagens():
    try:
        # Recebe a lista de imagens selecionadas
        imagens = request.json.get('imagens', [])
        if len(imagens) < 2:
            return jsonify({'error': 'Selecione pelo menos duas imagens'}), 400

        # Lista para armazenar as imagens carregadas
        images = []
        max_height = 0
        total_width = 0

        # Carrega todas as imagens e calcula dimensões
        for img_name in imagens:
            img_path = os.path.join(app.config['OUTPUT_FOLDER'], img_name)
            if not os.path.exists(img_path):
                continue
            
            img = Image.open(img_path)
            images.append(img)
            max_height = max(max_height, img.size[1])
            total_width += img.size[0]

        if not images:
            return jsonify({'error': 'Nenhuma imagem válida encontrada'}), 400

        # Cria uma nova imagem com as dimensões calculadas
        result = Image.new('RGB', (total_width, max_height))
        current_width = 0

        # Cola cada imagem na posição correta
        for img in images:
            # Redimensiona a altura mantendo a proporção
            if img.size[1] != max_height:
                ratio = max_height / img.size[1]
                new_width = int(img.size[0] * ratio)
                img = img.resize((new_width, max_height), Image.Resampling.LANCZOS)

            result.paste(img, (current_width, 0))
            current_width += img.size[0]

        # Gera um nome único para a imagem resultante
        output_filename = f'merged_{uuid.uuid4().hex[:8]}.jpg'
        # Usa a pasta Merge dentro da estrutura modular
        output_path = os.path.join(os.path.dirname(__file__), 'modules', 'data', 'merge', output_filename)

        # Salva a imagem resultante
        result.save(output_path, 'JPEG', quality=95)

        return jsonify({
            'success': True,
            'message': 'Imagens unidas com sucesso',
            'filename': output_filename,
            'url': url_for('merge_file', filename=output_filename)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Função para obter logs do sistema
def get_log_files():
    log_folder = "logs"
    log_files = []
    
    if os.path.exists(log_folder):
        log_files = sorted(glob.glob(os.path.join(log_folder, "*.log")), key=os.path.getmtime, reverse=True)
    
    return log_files

# Função para ler o conteúdo de um arquivo de log
def read_log_file(log_file):
    try:
        # Tenta ler com UTF-8 primeiro, depois fallback para latin-1
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(log_file, 'r', encoding='latin-1') as f:
                content = f.read()
        return content
    except Exception as e:
        return f"Erro ao ler arquivo de log: {str(e)}"

# Função para extrair informações de um arquivo de log
def parse_log_entry(log_file):
    try:
        filename = os.path.basename(log_file)
        match = re.search(r'processamento_(\d{8}_\d{6})\.log', filename)
        date_str = match.group(1) if match else "Unknown"
        
        # Formatar a data para exibição
        if date_str != "Unknown":
            date_obj = datetime.datetime.strptime(date_str, '%Y%m%d_%H%M%S')
            date_str = date_obj.strftime('%d/%m/%Y %H:%M:%S')
        
        content = read_log_file(log_file)
        
        # Determinar o nível do log com base no conteúdo
        level = "INFO"
        if "ERROR" in content:
            level = "ERROR"
        elif "WARNING" in content:
            level = "WARNING"
        
        return {
            'id': filename,
            'date': date_str,
            'level': level,
            'content': content,
            'path': log_file
        }
    except Exception as e:
        return {
            'id': os.path.basename(log_file),
            'date': 'Erro',
            'level': 'ERROR',
            'content': f"Erro ao processar arquivo de log: {str(e)}",
            'path': log_file
        }

# Rota para a página de logs
@app.route('/logs')
def logs():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Logs por página
    
    # Obtém os logs do processamento atual
    current_logs = [{
        'id': 'current_processing',
        'date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'level': 'INFO',
        'content': '\n'.join(processing_logs)
    }] if processing_logs else []
    
    # Obtém os logs dos arquivos
    log_files = get_log_files()
    file_logs = [parse_log_entry(log_file) for log_file in log_files]
    
    # Combina os logs atuais com os logs dos arquivos
    all_logs = current_logs + file_logs
    
    # Calcula a paginação
    total_logs = len(all_logs)
    total_pages = (total_logs + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    # Obtém os logs da página atual
    logs_page = all_logs[start:end]
    
    return render_template('logs.html',
                          logs=logs_page,
                          page=page,
                          total_pages=total_pages,
                          active_page='logs')

# Rota para excluir um log específico
@app.route('/delete_log', methods=['POST'])
def delete_log():
    log_id = request.form.get('log_id')
    log_path = os.path.join('logs', log_id)
    
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
            flash('Log excluído com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao excluir log: {str(e)}', 'error')
    else:
        flash('Arquivo de log não encontrado.', 'error')
    
    return redirect(url_for('logs'))

# Rota para excluir logs selecionados
@app.route('/delete_selected_logs', methods=['POST'])
def delete_selected_logs():
    selected_logs = request.form.get('selected_logs')
    
    if selected_logs:
        try:
            log_ids = json.loads(selected_logs)
            deleted_count = 0
            
            for log_id in log_ids:
                log_path = os.path.join('logs', log_id)
                if os.path.exists(log_path):
                    os.remove(log_path)
                    deleted_count += 1
            
            if deleted_count > 0:
                flash(f'{deleted_count} logs excluídos com sucesso!', 'success')
            else:
                flash('Nenhum log foi excluído.', 'warning')
        except Exception as e:
            flash(f'Erro ao excluir logs: {str(e)}', 'error')
    else:
        flash('Nenhum log selecionado.', 'warning')
    
    return redirect(url_for('logs'))

# Rota para excluir todos os logs
@app.route('/delete_all_logs', methods=['POST'])
def delete_all_logs():
    log_folder = "logs"
    
    if os.path.exists(log_folder):
        try:
            log_files = glob.glob(os.path.join(log_folder, "*.log"))
            deleted_count = 0
            
            for log_file in log_files:
                os.remove(log_file)
                deleted_count += 1
            
            if deleted_count > 0:
                flash(f'Todos os {deleted_count} logs foram excluídos com sucesso!', 'success')
            else:
                flash('Não havia logs para excluir.', 'info')
        except Exception as e:
            flash(f'Erro ao excluir todos os logs: {str(e)}', 'error')
    else:
        flash('Pasta de logs não encontrada.', 'error')
    
    return redirect(url_for('logs'))

# Rota para excluir logs por intervalo
@app.route('/delete_logs_range', methods=['POST'])
def delete_logs_range():
    start_index = request.form.get('start_index', type=int)
    end_index = request.form.get('end_index', type=int)
    
    if start_index and end_index:
        try:
            log_files = get_log_files()
            
            # Ajustar índices para base 0
            start_idx = start_index - 1
            end_idx = end_index - 1
            
            # Validar índices
            if start_idx < 0:
                start_idx = 0
            if end_idx >= len(log_files):
                end_idx = len(log_files) - 1
            
            if start_idx <= end_idx and start_idx < len(log_files):
                logs_to_delete = log_files[start_idx:end_idx+1]
                deleted_count = 0
                
                for log_file in logs_to_delete:
                    os.remove(log_file)
                    deleted_count += 1
                
                if deleted_count > 0:
                    flash(f'{deleted_count} logs excluídos com sucesso!', 'success')
                else:
                    flash('Nenhum log foi excluído.', 'warning')
            else:
                flash('Intervalo de logs inválido.', 'error')
        except Exception as e:
            flash(f'Erro ao excluir logs por intervalo: {str(e)}', 'error')
    else:
        flash('Parâmetros inválidos.', 'error')
    
    return redirect(url_for('logs'))

if __name__ == '__main__':
    port = 5000
    host = '0.0.0.0'
    print('\n' + '='*50)
    print('Iniciando servidor RePosture...')
    print(f'Interface web disponível em:')
    print(f' * Local:   http://localhost:{port}')
    print(f' * Rede:    http://{host}:{port}')
    print('Hot reload ativado - O servidor reiniciará automaticamente quando você modificar o código')
    print('='*50 + '\n')
    
    # Configuração completa para desenvolvimento com hot reload
    app.run(
        debug=True,           # Ativa o modo debug
        host=host,            # Permite acesso externo
        port=port,            # Porta do servidor
        use_reloader=True,    # Ativa o hot reload automático
        use_debugger=True,    # Ativa o debugger interativo
        threaded=True,        # Permite múltiplas requisições simultâneas
        extra_files=None      # Monitora arquivos adicionais (None = todos os .py)
    )

# Função para processar vídeo
def process_video_file(input_path):
    from modules.video_processor import VideoProcessor
    try:
        processor = VideoProcessor()
        output_path = processor.process_video(input_path, app.config['OUTPUT_FOLDER'])
        if output_path:
            return True, f"Vídeo processado com sucesso: {output_path}"
        return False, "Erro ao processar o vídeo"
    except Exception as e:
        return False, f"Erro durante o processamento do vídeo: {str(e)}"

# Atualiza a função de processamento para incluir vídeos
def processar_arquivo(filepath):
    global arquivo_atual
    try:
        # Verifica se é um arquivo de vídeo
        if filepath.lower().endswith(('.mp4', '.avi')):
            success, message = process_video_file(filepath)
            if not success:
                print(f"Erro no processamento do vídeo {filepath}: {message}")
                return False
            return True
        else:
            # Processamento existente para imagens
            return True
    except Exception as e:
        print(f"Erro no processamento do arquivo {filepath}: {e}")
        return False
    finally:
        arquivo_atual += 1