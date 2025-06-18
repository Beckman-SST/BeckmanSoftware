import cv2
import numpy as np

class FaceUtils:
    """
    Classe utilitária para operações relacionadas ao rosto, como aplicação de tarja.
    """
    
    def __init__(self, tarja_ratio=0.20, tarja_max_size=200):
        """
        Inicializa a classe de utilidades faciais.
        
        Args:
            tarja_ratio (float): Proporção da largura do frame para calcular tamanho mínimo da tarja (padrão: 0.20 = 20%)
            tarja_max_size (int): Tamanho máximo da tarja em pixels (padrão: 200px)
        """
        self.tarja_ratio = tarja_ratio
        self.tarja_max_size = tarja_max_size
    
    def apply_face_tarja(self, frame, face_landmarks=None, eye_landmarks=None):
        """
        Aplica tarja no rosto usando landmarks faciais ou dos olhos.
        Tenta aplicar uma tarja oval baseada no face_mesh, com fallback para tarja quadrada.
        
        Args:
            frame (numpy.ndarray): Frame onde a tarja será aplicada
            face_landmarks (dict): Dicionário com os landmarks do rosto (face_mesh)
            eye_landmarks (dict): Dicionário com os landmarks dos olhos (fallback)
            
        Returns:
            numpy.ndarray: Frame com a tarja aplicada
        """
        try:
            if face_landmarks and len(face_landmarks) > 5:
                # Usa landmarks faciais completos para criar uma tarja oval
                return self._apply_face_oval(frame, face_landmarks)
            elif eye_landmarks and len(eye_landmarks) > 0:
                # Usa landmarks dos olhos como fallback
                return self._apply_face_square(frame, eye_landmarks)
            else:
                return frame
                
        except Exception as e:
            print(f"Erro ao aplicar tarja facial: {str(e)}")
            return frame
    
    def _apply_face_square(self, frame, landmarks):
        """
        Aplica tarja quadrada baseada em landmarks faciais ou dos olhos.
        Ajusta o tamanho da tarja com base na distância estimada da pessoa.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            landmarks (dict): Dicionário com landmarks faciais ou dos olhos
            
        Returns:
            numpy.ndarray: Frame com tarja quadrada aplicada
        """
        if not landmarks:
            return frame
            
        h, w, _ = frame.shape
        
        # Procura por landmarks dos olhos (IDs 2 e 5 do MediaPose)
        left_eye = landmarks.get(2)  # LEFT_EYE
        right_eye = landmarks.get(5)  # RIGHT_EYE
        
        if left_eye and right_eye:
            # Calcula centro baseado nos dois olhos
            center_x = (left_eye[0] + right_eye[0]) // 2
            center_y = (left_eye[1] + right_eye[1]) // 2
            
            # Calcula a distância entre os olhos para estimar o tamanho do rosto
            eye_distance = np.sqrt((right_eye[0] - left_eye[0])**2 + (right_eye[1] - left_eye[1])**2)
            
            # Calcula tamanho da tarja proporcional à distância entre os olhos
            eye_ratio = eye_distance / w  # Proporção da distância dos olhos em relação à largura do frame
            
            # Ajusta o tamanho da tarja com base na distância entre os olhos
            scale_factor = 3.0  # Fator para garantir que a tarja cubra adequadamente o rosto
            tarja_size = max(100, min(int(eye_distance * scale_factor), self.tarja_max_size))
        elif left_eye or right_eye:
            # Se tiver apenas um olho, usa um tamanho padrão menor
            center_x, center_y = left_eye if left_eye else right_eye
            tarja_size = max(100, min(int(w * 0.15), self.tarja_max_size))  # Usa 15% da largura do frame
        else:
            # Tenta usar outros landmarks faciais disponíveis
            available_landmarks = [(x, y) for x, y in landmarks.values() if x > 0 and y > 0]
            if not available_landmarks:
                return frame
            
            # Calcula o centro e estima o tamanho com base na dispersão dos landmarks
            center_x = sum(x for x, y in available_landmarks) // len(available_landmarks)
            center_y = sum(y for x, y in available_landmarks) // len(available_landmarks)
            
            # Calcula a dispersão dos landmarks para estimar o tamanho do rosto
            x_coords = [x for x, y in available_landmarks]
            y_coords = [y for x, y in available_landmarks]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            face_size = max(x_max - x_min, y_max - y_min)
            
            # Ajusta o tamanho da tarja com base na dispersão dos landmarks
            tarja_size = max(100, min(int(face_size * 1.5), self.tarja_max_size))  # Fator 1.5 para garantir cobertura
        
        # Calcula coordenadas do quadrado centrado
        half_size = tarja_size // 2
        x_min = max(0, center_x - half_size)
        y_min = max(0, center_y - half_size)
        x_max = min(w, center_x + half_size)
        y_max = min(h, center_y + half_size)
        
        # Aplica retângulo preto quadrado
        frame_copy = frame.copy()
        cv2.rectangle(frame_copy, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        return frame_copy
    
    def _apply_face_oval(self, frame, face_landmarks):
        """
        Aplica tarja oval baseada nos landmarks do face_mesh.
        Cria uma elipse que se adapta ao formato do rosto.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            face_landmarks (dict): Dicionário com os landmarks do face_mesh
            
        Returns:
            numpy.ndarray: Frame com tarja oval aplicada
        """
        if not face_landmarks or len(face_landmarks) < 10:
            # Se não tiver landmarks suficientes, tenta usar o método quadrado
            return self._apply_face_square(frame, face_landmarks)
            
        try:
            # Extrai os pontos do contorno do rosto do face_mesh
            # Pontos do contorno facial no face_mesh (aproximadamente)
            contour_indices = [
                10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
            ]
            
            contour_points = []
            for idx in contour_indices:
                if idx in face_landmarks:
                    contour_points.append(face_landmarks[idx])
            
            if len(contour_points) < 5:  # Precisamos de pelo menos 5 pontos para uma elipse
                # Fallback para todos os pontos se não tivermos pontos de contorno suficientes
                contour_points = list(face_landmarks.values())
            
            # Converte para o formato numpy para cálculos
            contour_points = np.array(contour_points, dtype=np.int32)
            
            # Calcula o retângulo delimitador da elipse
            x_coords = contour_points[:, 0]
            y_coords = contour_points[:, 1]
            
            # Calcula o centro do rosto
            center_x = int(np.mean(x_coords))
            center_y = int(np.mean(y_coords))
            
            # Calcula os eixos da elipse
            # Adiciona uma margem para garantir que todo o rosto seja coberto
            margin_factor = 1.2  # 20% de margem
            axis_x = int((np.max(x_coords) - np.min(x_coords)) * margin_factor / 2)
            axis_y = int((np.max(y_coords) - np.min(y_coords)) * margin_factor / 2)
            
            # Garante tamanho mínimo e máximo para a elipse
            min_axis = 50  # Tamanho mínimo para cada eixo
            axis_x = max(min_axis, min(axis_x, self.tarja_max_size // 2))
            axis_y = max(min_axis, min(axis_y, self.tarja_max_size // 2))
            
            # Cria uma máscara do tamanho do frame
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)
            
            # Desenha a elipse preenchida na máscara
            cv2.ellipse(
                mask,
                (center_x, center_y),  # centro
                (axis_x, axis_y),      # eixos
                0,                     # ângulo
                0, 360,                # ângulo inicial e final
                (255),                 # cor (branco)
                -1                     # espessura (preenchido)
            )
            
            # Aplica a máscara ao frame (pinta de preto onde a máscara é branca)
            frame_with_mask = frame.copy()
            frame_with_mask[mask == 255] = (0, 0, 0)  # Preto
            
            return frame_with_mask
            
        except Exception as e:
            print(f"Erro ao aplicar tarja oval: {str(e)}")
            # Em caso de erro, volta para o método retangular
            return self._apply_face_square(frame, face_landmarks)