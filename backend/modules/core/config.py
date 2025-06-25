import os
import json
import tempfile

# Configurações padrão
DEFAULT_CONFIG = {
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
    'only_face_blur': False,  # Nova opção para processar apenas com tarja facial
    'resize_width': 800
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