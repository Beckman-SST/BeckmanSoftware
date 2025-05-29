import cv2
import os
import sys
import time
from datetime import datetime

# Importa os módulos necessários
from modules.core.config import ConfigManager
from modules.core.utils import ensure_directory_exists
from modules.processors.video_processor import VideoProcessor as ModularVideoProcessor

class VideoProcessor:
    def __init__(self, config_file=None):
        """
        Inicializa o processador de vídeos.
        
        Args:
            config_file (str): Caminho do arquivo de configuração
        """
        # Carrega as configurações
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()
        
        # Inicializa o processador modular
        self.processor = ModularVideoProcessor(self.config)
    
    def process_video(self, video_path, output_folder, progress_callback=None):
        """
        Processa um vídeo.
        
        Args:
            video_path (str): Caminho do vídeo a ser processado
            output_folder (str): Pasta onde o vídeo processado será salvo
            progress_callback (callable): Função de callback para reportar o progresso
            
        Returns:
            tuple: (sucesso, caminho do vídeo processado ou mensagem de erro)
        """
        # Verifica se o vídeo existe
        if not os.path.exists(video_path):
            return False, f"Arquivo não encontrado: {video_path}"
        
        # Verifica se a pasta de saída existe, se não, cria
        ensure_directory_exists(output_folder)
        
        # Processa o vídeo
        return self.processor.process_video(video_path, output_folder, progress_callback)
    
    def process_video_parallel(self, video_path, output_folder, num_workers=4, progress_callback=None):
        """
        Processa um vídeo usando processamento paralelo.
        
        Args:
            video_path (str): Caminho do vídeo a ser processado
            output_folder (str): Pasta onde o vídeo processado será salvo
            num_workers (int): Número de workers para processamento paralelo
            progress_callback (callable): Função de callback para reportar o progresso
            
        Returns:
            tuple: (sucesso, caminho do vídeo processado ou mensagem de erro)
        """
        # Verifica se o vídeo existe
        if not os.path.exists(video_path):
            return False, f"Arquivo não encontrado: {video_path}"
        
        # Verifica se a pasta de saída existe, se não, cria
        ensure_directory_exists(output_folder)
        
        # Processa o vídeo em paralelo
        return self.processor.process_video_parallel(video_path, output_folder, num_workers, progress_callback)
    
    def release(self):
        """
        Libera os recursos do processador.
        """
        self.processor.release()

# Função para processar um vídeo (compatibilidade com o código existente)
def process_video_file(video_path, output_folder, config_file=None, progress_callback=None):
    """
    Processa um vídeo.
    
    Args:
        video_path (str): Caminho do vídeo a ser processado
        output_folder (str): Pasta onde o vídeo processado será salvo
        config_file (str): Caminho do arquivo de configuração
        progress_callback (callable): Função de callback para reportar o progresso
        
    Returns:
        tuple: (sucesso, caminho do vídeo processado ou mensagem de erro)
    """
    processor = VideoProcessor(config_file)
    result = processor.process_video(video_path, output_folder, progress_callback)
    processor.release()
    return result