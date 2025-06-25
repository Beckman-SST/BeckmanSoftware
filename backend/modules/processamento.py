#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
import os
import sys
import argparse
import json
import tempfile
import time
from datetime import datetime

# Adiciona o diretório pai ao path para encontrar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os módulos necessários
from modules.core.config import ConfigManager
from modules.core.utils import ensure_directory_exists
from modules.processors.image_processor import ImageProcessor
from modules.processors.video_processor import VideoProcessor

def process_file(file_path, output_folder, config_file=None):
    """
    Processa um arquivo (imagem ou vídeo).
    
    Args:
        file_path (str): Caminho do arquivo a ser processado
        output_folder (str): Pasta onde o arquivo processado será salvo
        config_file (str): Caminho do arquivo de configuração
        
    Returns:
        tuple: (sucesso, caminho do arquivo processado ou mensagem de erro)
    """
    # Carrega as configurações
    config_manager = ConfigManager(config_file)
    config = config_manager.get_config()
    
    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        return False, f"Arquivo não encontrado: {file_path}"
    
    # Verifica se a pasta de saída existe, se não, cria
    ensure_directory_exists(output_folder)
    
    # Verifica se o arquivo é uma imagem ou um vídeo
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension in ['.jpg', '.jpeg', '.png', '.bmp']:
        # Verifica se deve processar apenas com tarja facial (modo operacional)
        if config.get('only_face_blur', False):
            # Usa o processador operacional que aplica apenas a tarja facial
            from modules.processors.operacional_tarja_processor import OperacionalTarjaProcessor
            processor = OperacionalTarjaProcessor(config)
            result = processor.process_image(file_path, output_folder)
            return result
        else:
            # Processa a imagem normalmente com análise de postura
            processor = ImageProcessor(config)
            result = processor.process_image(file_path, output_folder)
            processor.release()
            return result
    
    elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
        # Processa o vídeo
        processor = VideoProcessor(config)
        result = processor.process_video(file_path, output_folder)
        processor.release()
        return result
    
    else:
        return False, f"Formato de arquivo não suportado: {file_extension}"

def update_status(status_file, current_file, total_files, processed_files, start_time):
    """
    Atualiza o arquivo de status do processamento.
    
    Args:
        status_file (str): Caminho do arquivo de status
        current_file (str): Nome do arquivo atual
        total_files (int): Total de arquivos a serem processados
        processed_files (int): Número de arquivos já processados
        start_time (float): Tempo de início do processamento
    """
    try:
        # Calcula o progresso
        progress = (processed_files / total_files) * 100 if total_files > 0 else 0
        
        # Calcula o tempo decorrido
        elapsed_time = time.time() - start_time
        
        # Calcula o tempo médio por arquivo
        avg_time_per_file = elapsed_time / processed_files if processed_files > 0 else 0
        
        # Calcula o tempo estimado restante
        remaining_files = total_files - processed_files
        estimated_time_remaining = remaining_files * avg_time_per_file if avg_time_per_file > 0 else 0
        
        # Prepara os dados de status
        status_data = {
            'current_file': current_file,
            'total_files': total_files,
            'processed_files': processed_files,
            'progress': progress,
            'elapsed_time': elapsed_time,
            'estimated_time_remaining': estimated_time_remaining,
            'avg_time_per_file': avg_time_per_file,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Se o arquivo já existe, carrega o conteúdo atual para preservar outros campos
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    existing_data = json.load(f)
                    
                    # Preserva o campo 'config' se existir
                    if 'config' in existing_data:
                        status_data['config'] = existing_data['config']
            except:
                pass
        
        # Salva os dados de status
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    
    except Exception as e:
        print(f"Erro ao atualizar o status: {e}")

def main():
    # Configura o parser de argumentos
    parser = argparse.ArgumentParser(description='Processamento de imagens e vídeos para análise de postura.')
    parser.add_argument('input', help='Arquivo de entrada ou pasta contendo arquivos para processamento')
    parser.add_argument('-o', '--output', help='Pasta de saída para os arquivos processados')
    parser.add_argument('-c', '--config', help='Arquivo de configuração')
    args = parser.parse_args()
    
    # Define a pasta de saída padrão se não for especificada
    if not args.output:
        args.output = os.path.join(os.path.dirname(args.input), 'output')
    
    # Define o arquivo de status
    status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
    
    # Verifica se a entrada é um arquivo ou uma pasta
    if os.path.isfile(args.input):
        # Processa um único arquivo
        files_to_process = [args.input]
    elif os.path.isdir(args.input):
        # Processa todos os arquivos na pasta
        files_to_process = []
        for root, _, files in os.walk(args.input):
            for file in files:
                file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file_path)[1].lower()
                
                if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.mp4', '.avi', '.mov', '.mkv']:
                    files_to_process.append(file_path)
    else:
        print(f"Entrada inválida: {args.input}")
        sys.exit(1)
    
    # Verifica se há arquivos para processar
    if not files_to_process:
        print("Nenhum arquivo encontrado para processamento.")
        sys.exit(0)
    
    # Inicializa variáveis de controle
    total_files = len(files_to_process)
    processed_files = 0
    start_time = time.time()
    
    print(f"Iniciando processamento de {total_files} arquivo(s)...")
    
    # Processa cada arquivo
    for file_path in files_to_process:
        file_name = os.path.basename(file_path)
        print(f"Processando {file_name} ({processed_files + 1}/{total_files})...")
        
        # Atualiza o status
        update_status(status_file, file_name, total_files, processed_files, start_time)
        
        # Processa o arquivo
        success, result = process_file(file_path, args.output, args.config)
        
        if success:
            print(f"Arquivo processado com sucesso: {result}")
        else:
            print(f"Erro ao processar o arquivo: {result}")
        
        # Incrementa o contador de arquivos processados
        processed_files += 1
        
        # Atualiza o status
        update_status(status_file, file_name, total_files, processed_files, start_time)
    
    # Calcula o tempo total de processamento
    total_time = time.time() - start_time
    print(f"Processamento concluído em {total_time:.2f} segundos.")
    print(f"Arquivos processados: {processed_files}/{total_files}")

if __name__ == "__main__":
    main()