import os
import cv2
import numpy as np
import math
from datetime import datetime

def ensure_directory_exists(directory):
    """
    Garante que um diretório exista, criando-o se necessário.
    
    Args:
        directory (str): Caminho do diretório a ser verificado/criado
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def calculate_angle(a, b, c):
    """
    Calcula o ângulo entre três pontos.
    
    Args:
        a (tuple): Coordenadas do primeiro ponto (x, y)
        b (tuple): Coordenadas do segundo ponto (x, y) - ponto central
        c (tuple): Coordenadas do terceiro ponto (x, y)
        
    Returns:
        float: Ângulo em graus
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def calculate_angle_with_vertical(a, b):
    """
    Calcula o ângulo entre uma linha (definida por dois pontos) e a vertical.
    
    Args:
        a (tuple): Coordenadas do primeiro ponto (x, y)
        b (tuple): Coordenadas do segundo ponto (x, y)
        
    Returns:
        float: Ângulo em graus
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    
    # Ângulo com a vertical (eixo y)
    angle = math.degrees(math.atan2(dx, dy))
    
    # Normaliza o ângulo para o intervalo [0, 180]
    angle = abs(angle)
    if angle > 180:
        angle = 360 - angle
        
    return angle

def prolongar_reta(p1, p2, fator=0):
    """
    Retorna o ponto final da reta ou prolonga a reta se fator > 0.
    
    Args:
        p1 (tuple): Coordenadas do primeiro ponto (x, y)
        p2 (tuple): Coordenadas do segundo ponto (x, y)
        fator (int): Fator de prolongamento da reta. Se 0, retorna p2 sem prolongar.
        
    Returns:
        tuple: Coordenadas do ponto final ou prolongado (x, y)
    """
    x1, y1 = p1
    x2, y2 = p2
    
    # Se o fator for 0, apenas retorna o ponto final sem prolongar
    if fator == 0:
        return (int(x2), int(y2))
    
    # Calcula o vetor diretor da reta
    dx = x2 - x1
    dy = y2 - y1
    
    # Normaliza o vetor diretor
    comprimento = math.sqrt(dx**2 + dy**2)
    if comprimento > 0:
        dx = dx / comprimento
        dy = dy / comprimento
    
    # Prolonga a reta pelo fator especificado
    x_prolongado = int(x2 + dx * fator)
    y_prolongado = int(y2 + dy * fator)
    
    return (x_prolongado, y_prolongado)

# Dicionário global para armazenar as posições dos textos já desenhados no frame atual
_text_positions = {}

def adjust_text_position(frame, text, position, font, font_scale, color, thickness):
    """
    Ajusta a posição do texto para garantir que ele fique dentro dos limites do frame
    e não sobreponha outros textos já desenhados.
    
    Args:
        frame (numpy.ndarray): Frame onde o texto será desenhado
        text (str): Texto a ser desenhado
        position (tuple): Posição inicial do texto (x, y)
        font: Fonte do texto
        font_scale (float): Escala da fonte
        color (tuple): Cor do texto (B, G, R)
        thickness (int): Espessura do texto
        
    Returns:
        tuple: Posição ajustada do texto (x, y)
    """
    global _text_positions
    
    # Limpa o dicionário de posições se o frame mudou (verificando a soma dos pixels)
    frame_id = hash(str(frame.shape) + str(np.sum(frame[::50, ::50])))
    if not hasattr(adjust_text_position, "last_frame_id") or adjust_text_position.last_frame_id != frame_id:
        _text_positions = {}
        adjust_text_position.last_frame_id = frame_id
    
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    text_w, text_h = text_size
    text_x, text_y = position
    
    # Margem adicional ao redor do texto para evitar sobreposição
    margin = 15
    
    # Ajusta a posição horizontal para garantir que o texto fique dentro do frame
    if text_x + text_w > frame.shape[1]:
        text_x = frame.shape[1] - text_w - margin
    if text_x < 0:
        text_x = margin
        
    # Ajusta a posição vertical para garantir que o texto fique dentro do frame
    if text_y - text_h < 0:
        text_y = text_h + margin
    if text_y > frame.shape[0]:
        text_y = frame.shape[0] - margin
    
    # Verifica se a posição atual colide com algum texto já desenhado
    # e ajusta a posição vertical se necessário
    rect = (text_x - margin, text_y - text_h - margin, text_x + text_w + margin, text_y + margin)
    
    # Tenta encontrar uma posição que não colida com outros textos
    attempts = 0
    max_attempts = 10  # Limite de tentativas para evitar loop infinito
    
    while attempts < max_attempts:
        collision = False
        
        for existing_rect in _text_positions.values():
            # Verifica se há colisão entre os retângulos
            if (rect[0] < existing_rect[2] and rect[2] > existing_rect[0] and
                rect[1] < existing_rect[3] and rect[3] > existing_rect[1]):
                collision = True
                # Move o texto para baixo
                text_y += text_h + margin * 2
                # Atualiza o retângulo
                rect = (text_x - margin, text_y - text_h - margin, text_x + text_w + margin, text_y + margin)
                break
        
        if not collision or text_y > frame.shape[0] - margin:
            break
            
        attempts += 1
    
    # Se ainda estiver fora dos limites do frame após ajustes, força dentro dos limites
    if text_y > frame.shape[0] - margin:
        text_y = frame.shape[0] - margin
    
    # Armazena a posição final do texto
    _text_positions[text] = rect
    
    return (text_x, text_y)

def get_timestamp():
    """
    Retorna um timestamp formatado para uso em nomes de arquivos ou logs.
    
    Returns:
        str: Timestamp formatado
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def resize_frame(frame, target_width=None):
    """
    Redimensiona um frame mantendo a proporção.
    
    Args:
        frame (numpy.ndarray): Frame a ser redimensionado
        target_width (int, optional): Largura desejada. Se None, retorna o frame original.
        
    Returns:
        numpy.ndarray: Frame redimensionado
    """
    if target_width is None or target_width <= 0 or frame.shape[1] <= target_width:
        return frame
    
    scale = target_width / frame.shape[1]
    target_height = int(frame.shape[0] * scale)
    
    return cv2.resize(frame, (target_width, target_height))

def apply_moving_average(landmarks_history, current_landmarks, window_size=5):
    """
    Aplica média móvel aos landmarks para suavizar o movimento.
    
    Args:
        landmarks_history (list): Histórico de landmarks
        current_landmarks: Landmarks atuais
        window_size (int): Tamanho da janela da média móvel
        
    Returns:
        Landmarks suavizados
    """
    # Adiciona os landmarks atuais ao histórico
    landmarks_history.append(current_landmarks)
    
    # Mantém apenas os últimos 'window_size' frames
    if len(landmarks_history) > window_size:
        landmarks_history.pop(0)
    
    # Se não houver landmarks suficientes para a média móvel, retorna os landmarks atuais
    if len(landmarks_history) < 2:
        return current_landmarks
    
    # Calcula a média móvel
    smoothed_landmarks = current_landmarks
    
    # Implementação específica depende do formato dos landmarks
    # Esta é uma implementação genérica que deve ser adaptada conforme necessário
    
    return smoothed_landmarks