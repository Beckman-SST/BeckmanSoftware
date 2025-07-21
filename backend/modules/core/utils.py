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
    e não sobreponha outros textos já desenhados, com sistema avançado de anticolisão.
    
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
    original_x, original_y = position
    
    # Margem aumentada para melhor separação entre textos
    margin = 25  # Aumentado de 15 para 25 pixels
    padding = 10  # Padding adicional para o fundo do texto
    
    # Lista de posições candidatas em ordem de prioridade
    # Mantém proximidade com a articulação original
    candidate_positions = [
        (original_x, original_y),  # Posição original
        (original_x + 30, original_y),  # Direita
        (original_x - 30, original_y),  # Esquerda
        (original_x, original_y + 30),  # Abaixo
        (original_x, original_y - 30),  # Acima
        (original_x + 45, original_y + 15),  # Diagonal direita-baixo
        (original_x - 45, original_y + 15),  # Diagonal esquerda-baixo
        (original_x + 45, original_y - 15),  # Diagonal direita-cima
        (original_x - 45, original_y - 15),  # Diagonal esquerda-cima
    ]
    
    best_position = None
    min_distance = float('inf')
    
    for candidate_x, candidate_y in candidate_positions:
        # Ajusta a posição para garantir que fique dentro do frame
        text_x = max(margin, min(candidate_x, frame.shape[1] - text_w - margin))
        text_y = max(text_h + margin, min(candidate_y, frame.shape[0] - margin))
        
        # Calcula o retângulo com margem aumentada
        rect = (
            text_x - margin - padding, 
            text_y - text_h - margin - padding, 
            text_x + text_w + margin + padding, 
            text_y + margin + padding
        )
        
        # Verifica colisão com textos existentes
        has_collision = False
        for existing_rect in _text_positions.values():
            if (rect[0] < existing_rect[2] and rect[2] > existing_rect[0] and
                rect[1] < existing_rect[3] and rect[3] > existing_rect[1]):
                has_collision = True
                break
        
        # Se não há colisão, calcula a distância da posição original
        if not has_collision:
            distance = math.sqrt((text_x - original_x)**2 + (text_y - original_y)**2)
            if distance < min_distance:
                min_distance = distance
                best_position = (text_x, text_y, rect)
    
    # Se nenhuma posição candidata funcionou, usa algoritmo de fallback
    if best_position is None:
        text_x, text_y = original_x, original_y
        
        # Ajusta para dentro do frame
        text_x = max(margin, min(text_x, frame.shape[1] - text_w - margin))
        text_y = max(text_h + margin, min(text_y, frame.shape[0] - margin))
        
        # Algoritmo de fallback: move verticalmente até encontrar espaço
        attempts = 0
        max_attempts = 15  # Aumentado para mais tentativas
        step = text_h + margin
        
        while attempts < max_attempts:
            rect = (
                text_x - margin - padding, 
                text_y - text_h - margin - padding, 
                text_x + text_w + margin + padding, 
                text_y + margin + padding
            )
            
            collision = False
            for existing_rect in _text_positions.values():
                if (rect[0] < existing_rect[2] and rect[2] > existing_rect[0] and
                    rect[1] < existing_rect[3] and rect[3] > existing_rect[1]):
                    collision = True
                    break
            
            if not collision:
                best_position = (text_x, text_y, rect)
                break
            
            # Alterna entre mover para baixo e para cima
            if attempts % 2 == 0:
                text_y += step
            else:
                text_y = original_y - (step * ((attempts + 1) // 2))
            
            # Garante que permaneça dentro do frame
            text_y = max(text_h + margin, min(text_y, frame.shape[0] - margin))
            
            attempts += 1
        
        # Se ainda não encontrou posição, força uma posição válida
        if best_position is None:
            text_x = max(margin, min(original_x, frame.shape[1] - text_w - margin))
            text_y = max(text_h + margin, min(original_y, frame.shape[0] - margin))
            rect = (
                text_x - margin - padding, 
                text_y - text_h - margin - padding, 
                text_x + text_w + margin + padding, 
                text_y + margin + padding
            )
            best_position = (text_x, text_y, rect)
    
    final_x, final_y, final_rect = best_position
    
    # Armazena a posição final do texto com identificador único
    text_id = f"{text}_{len(_text_positions)}"
    _text_positions[text_id] = final_rect
    
    return (int(final_x), int(final_y))

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