import cv2 as cv
import numpy as np

# Função para redimensionar imagem mantendo a proporção
def resize_with_aspect_ratio(image, width=None, height=None, inter=cv.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv.resize(image, dim, interpolation=inter)

# Função para prolongar uma reta entre dois pontos
def prolongar_reta(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    # Não precisamos prolongar a reta, apenas retornamos o ponto final (vértice da caixa)
    return (int(x2), int(y2))

# Função para ajustar posição do texto para evitar sobreposição
def adjust_text_position(frame, text, position, bbox=None):
    h, w = frame.shape[:2]
    x, y = position
    
    # Se houver uma bbox, verificar se a posição está dentro
    if bbox:
        bx1, by1, bx2, by2 = bbox
        if x >= bx1 and x <= bx2 and y >= by1 and y <= by2:
            # Mover para cima da bbox
            y = by1 - 30 if by1 - 30 > 0 else by2 + 30
    
    # Garantir que o texto não saia da imagem
    (text_width, text_height), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    x = max(10, min(x, w - text_width - 10))
    y = max(text_height + 10, min(y, h - 10))
    
    return (x, y)

# Função para desenhar detecções de eletrônicos (com transparência)
def draw_electronics_detections(frame, detections, show_electronics=False):
    # Se não há detecções, retorna o frame sem modificações
    if not detections:
        return frame
        
    # Se a visualização de eletrônicos estiver desativada, retorna o frame sem modificações
    # O cálculo dos ângulos dos olhos será feito independentemente
    if not show_electronics:
        return frame
        
    # Cria uma cópia do frame para desenhar as detecções
    overlay = frame.copy()
    
    # Desenha cada detecção
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        cv.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{detection['class']}: {detection['confidence']:.2f}"
        cv.putText(overlay, label, (x1, y1-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Aplica transparência
    alpha = 0.7
    cv.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    return frame