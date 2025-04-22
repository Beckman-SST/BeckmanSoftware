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

# Configurações da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'beckman_project_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'Output'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'mp4', 'avi'}
app.config['CONFIG_FILE'] = 'config.json'

# Variáveis globais para controle do processamento
processamento_ativo = False
cancelar_processamento = False
status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
arquivo_atual = 0
total_files = 0
tempos_processamento = []

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
for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

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
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Procura por mensagens de erro no log
        error_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ERROR - (.+)'
        errors = re.findall(error_pattern, content)
        return errors
    except Exception as e:
        print(f"Erro ao extrair erros do log: {e}")
        return []

# Função para processar os arquivos em uma thread separada
def processar_arquivos(file_paths):
    global processamento_ativo, cancelar_processamento, arquivo_atual, total_files, tempos_processamento
    
    processamento_ativo = True
    cancelar_processamento = False
    
    # Processa cada arquivo
    total_files = len(file_paths)
    tempos_processamento = []
    arquivo_atual = 0
    tempo_inicio = time.time()

    for i, file_path in enumerate(file_paths):
        if cancelar_processamento:
            break
            
        arquivo_atual = i + 1
        arquivo_start_time = time.time()
        
        # Atualiza status para o processo filho
        atualizar_status_processamento({
            'deve_continuar': True,
            'arquivo_atual': file_path
        })
        
        try:
            processo = subprocess.Popen([sys.executable, "processamento.py", file_path],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            
            while processo.poll() is None:
                if cancelar_processamento:
                    atualizar_status_processamento({'deve_continuar': False})
                    processo.terminate()
                    break
                time.sleep(0.1)
            
            if not cancelar_processamento:
                stdout, stderr = processo.communicate()
                if processo.returncode != 0:
                    try:
                        erro_msg = stderr.decode('utf-8')
                    except UnicodeDecodeError:
                        erro_msg = stderr.decode('latin-1')
                    print(f"Erro ao processar {os.path.basename(file_path)}:\n{erro_msg}")
                    flash(f"Erro ao processar {os.path.basename(file_path)}: {erro_msg}", "error")
                    continue
                
                # Verifica o arquivo de log mais recente para extrair erros
                log_files = get_log_files()
                if log_files:
                    latest_log = log_files[0]  # O mais recente está no topo
                    errors = extract_errors_from_log(latest_log)
                    if errors:
                        for error in errors:
                            if "Não foi possível detectar os landmarks principais do corpo" in error:
                                flash(f"Erro ao processar {os.path.basename(file_path)}: {error}", "error")
                                break
        except Exception as e:
            print(f"Erro ao executar processamento: {str(e)}")
            flash(f"Erro ao executar processamento de {os.path.basename(file_path)}: {str(e)}", "error")
            continue
            
        tempo_arquivo = time.time() - arquivo_start_time
        tempos_processamento.append(tempo_arquivo)
        
        # Atualiza o tempo médio e estimativa restante após cada arquivo processado
        tempo_medio = sum(tempos_processamento) / len(tempos_processamento)
        arquivos_restantes = total_files - (i + 1)
        tempo_restante = int(tempo_medio * arquivos_restantes) if tempo_medio > 0 else 0
        
        print(f"Progresso: {arquivo_atual}/{total_files} - Tempo restante: {tempo_restante} segundos")

    # Limpa o arquivo de status
    if os.path.exists(status_file):
        try:
            os.remove(status_file)
        except:
            pass

    processamento_ativo = False

# Rota principal
@app.route('/')
def index():
    # Lista os arquivos processados
    processed_files = []
    error_files = []
    
    if os.path.exists(app.config['OUTPUT_FOLDER']):
        all_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER']) 
                    if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f))]
        
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
            file.save(file_path)
            valid_files.append(file_path)
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
    global arquivo_atual, total_files, tempos_processamento
    
    status_info = {
        'ativo': processamento_ativo,
        'cancelando': cancelar_processamento
    }
    
    if processamento_ativo and arquivo_atual > 0:
        # Calcula tempo médio e estimativa restante
        tempo_medio = sum(tempos_processamento) / len(tempos_processamento) if tempos_processamento else 0
        arquivos_restantes = total_files - arquivo_atual
        tempo_restante = int(tempo_medio * arquivos_restantes) if tempo_medio > 0 else 0
        
        # Adiciona informações de progresso
        status_info.update({
            'arquivo_atual': arquivo_atual,
            'total_arquivos': total_files,
            'progresso': (arquivo_atual / total_files) * 100 if total_files > 0 else 0,
            'tempo_restante': tempo_restante
        })
    
    return status_info

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
            os.remove(file_path)
    
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
        with open(log_file, 'r', encoding='utf-8') as f:
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
    
    log_files = get_log_files()
    total_logs = len(log_files)
    total_pages = (total_logs + per_page - 1) // per_page
    
    # Paginação
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_logs)
    current_logs = log_files[start_idx:end_idx]
    
    # Processar logs para exibição
    logs_data = [parse_log_entry(log_file) for log_file in current_logs]
    
    return render_template('logs.html', logs=logs_data, page=page, total_pages=total_pages)

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
    app.run(debug=True, host='0.0.0.0', port=5000)