import cv2 as cv
import mediapipe as mp
import os
from typing import Optional

class VideoProcessor:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_video(self, input_path: str, output_folder: str) -> Optional[str]:
        """Processa um vídeo, detectando landmarks e salvando o resultado.

        Args:
            input_path: Caminho do vídeo de entrada
            output_folder: Pasta onde o vídeo processado será salvo

        Returns:
            str: Caminho do vídeo processado ou None se houver erro
        """
        if not os.path.exists(input_path):
            print(f"Erro: Arquivo {input_path} não encontrado.")
            return None

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        cap = cv.VideoCapture(input_path)
        if not cap.isOpened():
            print("Erro ao abrir o vídeo.")
            return None

        # Obtém propriedades do vídeo
        frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv.CAP_PROP_FPS))

        # Configura o arquivo de saída
        output_path = os.path.join(output_folder, f"processed_{os.path.basename(input_path)}")
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

        with self.mp_holistic.Holistic(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as holistic:

            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                # Processa o frame
                frame.flags.writeable = False
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                results = holistic.process(frame)

                # Desenha os landmarks
                frame.flags.writeable = True
                frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

                # Desenha os landmarks da pose
                if results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        self.mp_holistic.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

                # Escreve o frame processado
                out.write(frame)

                # Mostra o progresso
                print(f"Processando frame... {int(cap.get(cv.CAP_PROP_POS_FRAMES))}", end='\r')

        # Libera os recursos
        cap.release()
        out.release()
        print(f"\nVídeo processado salvo em: {output_path}")
        return output_path