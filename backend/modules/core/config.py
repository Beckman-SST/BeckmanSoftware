import os
import json
import tempfile

# Configurações padrão - OTIMIZADAS PARA MELHOR QUALIDADE DE LANDMARKS
DEFAULT_CONFIG = {
    # === PARÂMETROS DE DETECÇÃO OTIMIZADOS ===
    'min_detection_confidence': 0.85,  # MELHORADO: Era 0.80 (+6% rigor na detecção)
    'min_tracking_confidence': 0.85,   # MELHORADO: Era 0.80 (+6% rigor no rastreamento)
    'yolo_confidence': 0.65,
    'moving_average_window': 5,
    'show_face_blur': True,
    'show_electronics': True,
    'show_angles': True,
    'show_upper_body': True,
    'show_lower_body': True,
    'processing_mode': 'auto',  # 'auto', 'upper_only', 'lower_only'
    'only_face_blur': False,  # Nova opção para processar apenas com tarja facial
    'resize_width': 800,
    
    # === CONFIGURAÇÕES DE PRÉ-PROCESSAMENTO OTIMIZADAS ===
    'enable_clahe': True,  # Habilita CLAHE (Contrast Limited Adaptive Histogram Equalization)
    'clahe_clip_limit': 2.2,  # MELHORADO: Era 2.0 (+10% contraste para melhor detecção)
    'clahe_tile_grid_size': 8,  # Tamanho da grade de tiles para CLAHE (4-16, padrão: 8)
    
    # === CONFIGURAÇÕES DE SUAVIZAÇÃO TEMPORAL AVANÇADA ===
    'enable_advanced_smoothing': True,  # Habilita suavização temporal avançada
    'enable_kalman_filter': True,  # Habilita filtro de Kalman para landmarks
    'enable_outlier_detection': True,  # Habilita detecção de outliers
    'enable_weighted_average': True,  # Habilita média móvel ponderada
    
    # === PARÂMETROS DO FILTRO DE KALMAN OTIMIZADOS ===
    'kalman_process_noise': 0.005,  # MELHORADO: Era 0.01 (-50% ruído, mais conservador)
    'kalman_measurement_noise': 0.08,  # MELHORADO: Era 0.1 (-20% ruído, mais confiante)
    
    # === PARÂMETROS DA DETECÇÃO DE OUTLIERS OTIMIZADOS ===
    'outlier_velocity_threshold': 35.0,  # MELHORADO: Era 50.0 (-30% threshold, mais sensível)
    'outlier_acceleration_threshold': 75.0,  # MELHORADO: Era 100.0 (-25% threshold, mais sensível)
    
    # === PARÂMETROS DA MÉDIA MÓVEL PONDERADA OTIMIZADOS ===
    'weighted_window_size': 7,  # MELHORADO: Era 5 (+40% histórico para melhor suavização)
    'weighted_decay_factor': 0.85,  # MELHORADO: Era 0.8 (+6% peso nos dados recentes)
    
    # === NOVOS PARÂMETROS DE QUALIDADE DE LANDMARKS ===
    'landmark_visibility_threshold': 0.5,  # NOVO: Threshold mínimo de visibilidade (era implícito 0.3)
    'landmark_confidence_threshold': 0.7,  # NOVO: Threshold mínimo de confiança (era implícito 0.5)
    'enable_anatomical_validation': False,  # NOVO: Habilita validação anatômica (será implementado)
    'enable_smart_interpolation': False,   # NOVO: Habilita interpolação inteligente (será implementado)
}

class ConfigManager:
    def __init__(self, config_file=None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_file: Caminho para o arquivo de configuração. Se None, usa o arquivo temporário padrão.
        """
        self.config_file = config_file
        if self.config_file is None:
            self.config_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
        self.config = self.load_config()
    
    def load_config(self):
        """
        Carrega as configurações do arquivo ou usa as padrões.
        
        Returns:
            dict: Configurações carregadas
        """
        config = DEFAULT_CONFIG.copy()
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    status_data = json.load(f)
                    if 'config' in status_data:
                        config = status_data['config']
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
        
        return config
    
    def save_config(self, config=None):
        """
        Salva as configurações no arquivo.
        
        Args:
            config: Configurações a serem salvas. Se None, usa as configurações atuais.
            
        Returns:
            bool: True se as configurações foram salvas com sucesso, False caso contrário.
        """
        if config is not None:
            self.config = config
            
        try:
            # Se o arquivo já existe, carrega o conteúdo atual para preservar outros campos
            status_data = {}
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        status_data = json.load(f)
                except:
                    pass
            
            # Atualiza apenas o campo 'config'
            status_data['config'] = self.config
            
            with open(self.config_file, 'w') as f:
                json.dump(status_data, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_config(self):
        """
        Retorna as configurações atuais.
        
        Returns:
            dict: Configurações atuais
        """
        return self.config
    
    def update_config(self, new_config):
        """
        Atualiza as configurações com novos valores.
        
        Args:
            new_config: Novas configurações a serem mescladas com as atuais
            
        Returns:
            bool: True se as configurações foram atualizadas com sucesso, False caso contrário.
        """
        self.config.update(new_config)
        return self.save_config()
    
    def reset_to_default(self):
        """
        Redefine as configurações para os valores padrão.
        
        Returns:
            bool: True se as configurações foram redefinidas com sucesso, False caso contrário.
        """
        self.config = DEFAULT_CONFIG.copy()
        return self.save_config()