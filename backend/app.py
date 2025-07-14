import os
import sys
import time
import threading
import subprocess
import json
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
from modules.processors.video_processor import VideoProcessor

# Função para processar vídeo (wrapper para manter compatibilidade)
def process_video_file(input_path):
    try:
        config = load_config()
        processor = VideoProcessor(config)
        success, result = processor.process_video(input_path, app.config['OUTPUT_FOLDER'])
        if success:
            return True, f"Vídeo processado com sucesso: {result}"
        return False, result
    except Exception as e:
        return False, f"Erro durante o processamento do vídeo: {str(e)}"

# Configurações da aplicação
app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
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



# Configurações padrão
default_config = {
    'min_detection_confidence': 0.70,
    'min_tracking_confidence': 0.60,
    'yolo_confidence': 0.50,
    'moving_average_window': 5,
    'show_face_blur': True,
    'show_electronics': False,
    'show_angles': True,
    'show_upper_body': True,
    'show_lower_body': True,
    'process_lower_body': True,
    'only_face_blur': False,  # Nova opção para processar apenas com tarja facial
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



# Função para processar os arquivos em uma thread separada
# Lista thread-safe para armazenar mensagens de erro
error_messages = []

def adicionar_erro(mensagem):
    """Adiciona uma mensagem de erro à lista thread-safe"""
    error_messages.append(mensagem)

def processar_arquivos(file_paths, is_operacional=False):
    global processamento_ativo, cancelar_processamento, arquivo_atual, total_files, tempos_processamento
    
    processamento_ativo = True
    cancelar_processamento = False
    error_messages.clear()  # Limpa mensagens de erro anteriores
    
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

    for i, file_path in enumerate(file_paths):
        if cancelar_processamento:
            break
            
        arquivo_atual = i + 1
        arquivo_start_time = time.time()
        filename = os.path.basename(file_path)
        
        # Atualiza status
        atualizar_status_processamento({
            'deve_continuar': True,
            'arquivo_atual': file_path
        })
        
        try:
            # Verifica se é um arquivo de vídeo
            if file_path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                # Apenas detecção, desenho dos landmarks e salvamento do vídeo
                success, message = process_video_file(file_path)
                if not success:
                    adicionar_erro(message)
                    continue
            else:
                # Processamento de imagens usando o módulo modular
                output_folder = app.config['OUTPUT_FOLDER']
                processo = subprocess.Popen([sys.executable, os.path.join(os.path.dirname(__file__), "modules", "processamento.py"), file_path, "-o", output_folder],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
                
                while processo.poll() is None:
                    if cancelar_processamento:
                        processo.terminate()
                        break
                    time.sleep(0.1)
                
                if not cancelar_processamento:
                    stdout, stderr = processo.communicate()
                    
                    # Verifica o código de retorno do processo
                    if processo.returncode != 0:
                        erro = stderr.decode('utf-8', errors='ignore')
                        adicionar_erro(f"Erro ao processar {filename}: {erro}")
            
            # Remove o arquivo de upload após processamento
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Erro ao remover arquivo {file_path}: {e}")
            
            # Calcula tempo de processamento
            tempo_processamento = time.time() - arquivo_start_time
            tempos_processamento.append(tempo_processamento)
                
        except Exception as e:
            adicionar_erro(f"Erro inesperado ao processar {filename}: {str(e)}")
    
    tempo_total = time.time() - tempo_inicio
    
    # Se foi um processamento operacional, restaura a configuração para o valor padrão
    if is_operacional:
        config = load_config()
        config['only_face_blur'] = False
        save_config_to_file(config)
    
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
    return send_from_directory(app.static_folder, 'index.html')

# API para carregar configurações
@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        current_config = load_config()
        return jsonify({
            'success': True,
            'config': current_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para salvar configurações
@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dados de configuração não fornecidos'
            }), 400
        
        # Valida e processa as configurações
        new_config = {
            'min_detection_confidence': float(data.get('min_detection_confidence', default_config['min_detection_confidence'])),
            'min_tracking_confidence': float(data.get('min_tracking_confidence', default_config['min_tracking_confidence'])),
            'yolo_confidence': float(data.get('yolo_confidence', default_config['yolo_confidence'])),
            'moving_average_window': int(data.get('moving_average_window', default_config['moving_average_window'])),
            'show_face_blur': bool(data.get('show_face_blur', False)),
            'show_electronics': bool(data.get('show_electronics', False)),
            'show_angles': bool(data.get('show_angles', False)),
            'show_upper_body': bool(data.get('show_upper_body', False)),
            'show_lower_body': bool(data.get('show_lower_body', False)),
            'process_lower_body': bool(data.get('process_lower_body', False)),
            'only_face_blur': bool(data.get('only_face_blur', False)),
            'resize_width': int(data.get('resize_width', default_config['resize_width']))
        }
        
        # Salva as configurações
        if save_config_to_file(new_config):
            return jsonify({
                'success': True,
                'message': 'Configurações salvas com sucesso!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao salvar configurações'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para resetar configurações para valores padrão de fábrica
@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    try:
        # Salva as configurações padrão de fábrica
        if save_config_to_file(default_config.copy()):
            return jsonify({
                'success': True,
                'message': 'Configurações resetadas para valores padrão de fábrica!',
                'config': default_config
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erro ao resetar configurações'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para upload de arquivos
@app.route('/api/upload', methods=['POST'])
def upload_file():
    global processamento_ativo
    
    try:
        if processamento_ativo:
            return jsonify({
                'success': False,
                'error': 'Já existe um processamento em andamento. Aguarde a conclusão.'
            }), 400
        
        # Verifica se há arquivos no request
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        files = request.files.getlist('files')
        
        # Verifica se algum arquivo foi selecionado
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        # Verifica o tipo de processamento
        processing_type = request.form.get('processing_type', 'executivo')
        is_operacional = processing_type == 'operacional'
        is_videos = processing_type == 'videos'
        
        # Se for processamento operacional, atualiza a configuração para usar apenas tarja facial
        if is_operacional:
            config = load_config()
            config['only_face_blur'] = True
            save_config_to_file(config)
        # Se for processamento de vídeos, pode ter configurações específicas no futuro
        elif is_videos:
            # Configurações específicas para processamento de vídeos podem ser adicionadas aqui
            pass
        
        # Lista para armazenar os caminhos dos arquivos válidos
        valid_files = []
        errors = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file.save(file_path)
                    valid_files.append(file_path)
                except Exception as e:
                    errors.append(f'Erro ao salvar arquivo {filename}: {e}')
            else:
                errors.append(f'Arquivo {file.filename} não permitido. Use apenas imagens (jpg, jpeg, png) ou vídeos (mp4, avi).')
        
        if valid_files:
            # Inicia o processamento em uma thread separada
            threading.Thread(target=processar_arquivos, args=(valid_files, is_operacional)).start()
            
            message = f'{len(valid_files)} arquivo(s) enviado(s) para processamento'
            if is_operacional:
                message += ' operacional com tarja facial'
            elif is_videos:
                message += ' de vídeos'
            
            return jsonify({
                'success': True,
                'message': message,
                'files_count': len(valid_files),
                'errors': errors
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo válido foi enviado',
                'errors': errors
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para cancelar o processamento
@app.route('/api/cancel', methods=['POST'])
def cancelar():
    global cancelar_processamento
    
    try:
        if processamento_ativo:
            cancelar_processamento = True
            return jsonify({
                'success': True,
                'message': 'Solicitação de cancelamento enviada. Aguarde...'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Não há processamento ativo para cancelar'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para verificar o status do processamento
@app.route('/api/status')
def status():
    global arquivo_atual, total_files, tempos_processamento, error_messages
    
    status_info = {
        'ativo': processamento_ativo,
        'processing': processamento_ativo,  # Compatibilidade com frontend antigo
        'cancelando': cancelar_processamento,
        'erros': error_messages[:],  # Envia uma cópia da lista de erros
        'arquivos_processados': []
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

# API para limpar os arquivos temporários
@app.route('/api/cleanup', methods=['POST'])
def limpar():
    try:
        if processamento_ativo:
            return jsonify({
                'success': False,
                'error': 'Não é possível limpar enquanto há um processamento em andamento'
            }), 400
        
        errors = []
        removed_count = 0
        
        # Limpa a pasta de uploads
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    removed_count += 1
                except Exception as e:
                    errors.append(f'Erro ao remover arquivo temporário {filename}: {e}')
        
        return jsonify({
            'success': True,
            'message': f'Arquivos temporários removidos com sucesso ({removed_count} arquivos)',
            'removed_count': removed_count,
            'errors': errors
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para abrir a pasta de output
@app.route('/api/open-folder')
def abrir_pasta():
    try:
        output_path = os.path.abspath(app.config['OUTPUT_FOLDER'])
        if os.path.exists(output_path):
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            elif os.name == 'posix':  # macOS e Linux
                subprocess.Popen(['open', output_path] if sys.platform == 'darwin' else ['xdg-open', output_path])
            return jsonify({'success': True, 'path': output_path})
        else:
            return jsonify({
                'success': False,
                'error': 'Pasta de saída não encontrada'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para listar arquivos processados
@app.route('/api/files')
def list_files():
    try:
        processed_images = []
        processed_videos = []
        error_files = []
        
        if os.path.exists(app.config['OUTPUT_FOLDER']):
            image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
            video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
            all_files = [f for f in os.listdir(app.config['OUTPUT_FOLDER'])
                         if os.path.isfile(os.path.join(app.config['OUTPUT_FOLDER'], f))]
            
            for f in all_files:
                file_path = os.path.join(app.config['OUTPUT_FOLDER'], f)
                file_stats = os.stat(file_path)
                file_info = {
                    'name': f,
                    'size': file_stats.st_size,
                    'modified': file_stats.st_mtime,
                    'url': url_for('output_file', filename=f)
                }
                
                if f.startswith('error_'):
                    error_files.append(file_info)
                elif f.lower().endswith(image_extensions):
                    processed_images.append(file_info)
                elif f.lower().endswith(video_extensions):
                    processed_videos.append(file_info)
        
        return jsonify({
            'success': True,
            'images': processed_images,
            'videos': processed_videos,
            'errors': error_files,
            'total': len(processed_images) + len(processed_videos) + len(error_files)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para obter URL de arquivo
@app.route('/api/file-url/<filename>')
def get_file_url(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return jsonify({
                'success': True,
                'url': url_for('output_file', filename=filename),
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API para verificar saúde do servidor
@app.route('/api/health')
def health_check():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'processing_active': processamento_ativo,
        'timestamp': time.time()
    })

# API para união de imagens
@app.route('/api/merge-images', methods=['POST'])
def unir_imagens():
    try:
        # Recebe a lista de imagens selecionadas
        data = request.get_json()
        if not data or 'images' not in data:
            return jsonify({'success': False, 'error': 'Lista de imagens não fornecida'}), 400
            
        imagens = data.get('images', [])
        if len(imagens) < 2:
            return jsonify({'success': False, 'error': 'Selecione pelo menos duas imagens'}), 400

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
            return jsonify({'success': False, 'error': 'Nenhuma imagem válida encontrada'}), 400

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
        return jsonify({'success': False, 'error': str(e)}), 500

# Rota para servir arquivos da pasta Merge
@app.route('/merge/<filename>')
def merge_file(filename):
    return send_from_directory(app.config['MERGE_FOLDER'], filename)

# API para criar múltiplas colagens
@app.route('/api/create-collages', methods=['POST'])
def create_collages():
    try:
        # Recebe os grupos de imagens
        data = request.get_json()
        if not data or 'groups' not in data:
            return jsonify({'success': False, 'error': 'Grupos de imagens não fornecidos'}), 400
            
        groups = data.get('groups', [])
        if not groups:
            return jsonify({'success': False, 'error': 'Nenhum grupo de imagens fornecido'}), 400

        created_collages = []
        
        # Processa cada grupo
        for group_index, group in enumerate(groups):
            if 'images' not in group or not group['images']:
                continue
                
            imagens = group['images']
            if len(imagens) < 1:
                continue

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
                continue

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

            # Gera um nome único para a colagem
            timestamp = int(time.time())
            output_filename = f'collage_{timestamp}_{group_index + 1}_{uuid.uuid4().hex[:6]}.jpg'
            output_path = os.path.join(app.config['MERGE_FOLDER'], output_filename)

            # Salva a colagem
            result.save(output_path, 'JPEG', quality=95)
            
            created_collages.append({
                'filename': output_filename,
                'url': url_for('merge_file', filename=output_filename),
                'images_count': len(images)
            })

        if not created_collages:
            return jsonify({'success': False, 'error': 'Nenhuma colagem pôde ser criada'}), 400

        return jsonify({
            'success': True,
            'message': f'{len(created_collages)} colagens criadas com sucesso',
            'collages': created_collages
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500






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

def process_all_videos():
    """
    Process all videos in the VIDEOS_FOLDER and save results to OUTPUT_FOLDER.
    """
    from modules.processors.video_processor import VideoProcessor
    input_folder = app.config['VIDEOS_FOLDER']
    output_folder = app.config['OUTPUT_FOLDER']
    config = load_config()
    processor = VideoProcessor(config)
    video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not video_files:
        print("Nenhum vídeo encontrado na pasta de entrada.")
        return
    for video_file in video_files:
        input_path = os.path.join(input_folder, video_file)
        print(f"\nProcessando vídeo: {video_file}")
        success, output_path = processor.process_video(input_path, output_folder)
        if success:
            print(f"Processamento concluído com sucesso!")
        else:
            print(f"Erro ao processar o vídeo {video_file}: {output_path}")