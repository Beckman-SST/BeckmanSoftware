import cv2
import os
import time
import numpy as np
import mediapipe as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.utils import ensure_directory_exists, get_timestamp

class VideoProcessor:
    def __init__(self, config):
        """
        Inicializa o processador de vídeos.
        
        Args:
            config (dict): Configurações para o processamento
        """
        self.config = config
        # Inicializa MediaPipe para detecção de pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=config.get('min_detection_confidence', 0.5),
            min_tracking_confidence=config.get('min_tracking_confidence', 0.5)
        )
    
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
        try:
            # Verifica se o vídeo existe
            if not os.path.exists(video_path):
                return False, f"Arquivo não encontrado: {video_path}"
            
            # Verifica se a pasta de saída existe, se não, cria
            ensure_directory_exists(output_folder)
            
            # Abre o vídeo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, f"Não foi possível abrir o vídeo: {video_path}"
            
            # Obtém as propriedades do vídeo
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Redimensiona o vídeo se necessário
            resize_width = self.config.get('resize_width')
            if resize_width and resize_width > 0 and width > resize_width:
                scale = resize_width / width
                width = resize_width
                height = int(height * scale)
            
            # Define o nome do arquivo de saída
            output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_processado.mp4'
            output_path = os.path.join(output_folder, output_filename)
            
            # Define o codec e cria o objeto VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Processa o vídeo
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Processa o frame
                processed_frame = self._process_frame(frame, video_path, output_folder, frame_count)
                
                # Escreve o frame processado no vídeo de saída
                out.write(processed_frame)
                
                # Atualiza o contador de frames e o progresso
                frame_count += 1
                if progress_callback and total_frames > 0:
                    progress = (frame_count / total_frames) * 100
                    elapsed_time = time.time() - start_time
                    remaining_frames = total_frames - frame_count
                    
                    # Estima o tempo restante
                    if frame_count > 0 and elapsed_time > 0:
                        time_per_frame = elapsed_time / frame_count
                        estimated_time_remaining = remaining_frames * time_per_frame
                    else:
                        estimated_time_remaining = 0
                    
                    progress_callback(progress, estimated_time_remaining)
            
            # Libera os recursos
            cap.release()
            out.release()
            
            return True, output_path
        
        except Exception as e:
            return False, f"Erro ao processar o vídeo: {str(e)}"
        
        finally:
            # Garante que os recursos sejam liberados mesmo em caso de erro
            if 'cap' in locals() and cap is not None:
                cap.release()
            if 'out' in locals() and out is not None:
                out.release()
    
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
        try:
            # Verifica se o vídeo existe
            if not os.path.exists(video_path):
                return False, f"Arquivo não encontrado: {video_path}"
            
            # Verifica se a pasta de saída existe, se não, cria
            ensure_directory_exists(output_folder)
            
            # Cria uma pasta temporária para os frames processados
            temp_folder = os.path.join(output_folder, f"temp_{get_timestamp()}")
            ensure_directory_exists(temp_folder)
            
            # Abre o vídeo
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False, f"Não foi possível abrir o vídeo: {video_path}"
            
            # Obtém as propriedades do vídeo
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Redimensiona o vídeo se necessário
            resize_width = self.config.get('resize_width')
            if resize_width and resize_width > 0 and width > resize_width:
                scale = resize_width / width
                width = resize_width
                height = int(height * scale)
            
            # Define o nome do arquivo de saída
            output_filename = os.path.splitext(os.path.basename(video_path))[0] + '_processado.mp4'
            output_path = os.path.join(output_folder, output_filename)
            
            # Extrai os frames do vídeo
            frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Redimensiona o frame se necessário
                if resize_width and resize_width > 0 and frame.shape[1] > resize_width:
                    scale = resize_width / frame.shape[1]
                    frame = cv2.resize(frame, (resize_width, int(frame.shape[0] * scale)))
                
                # Salva o frame em disco para processamento posterior
                frame_path = os.path.join(temp_folder, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append(frame_path)
                
                frame_count += 1
            
            # Libera o vídeo de entrada
            cap.release()
            
            # Processa os frames em paralelo
            processed_frames = []
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # Submete as tarefas para processamento
                future_to_frame = {executor.submit(self._process_frame_file, frame_path): i 
                                  for i, frame_path in enumerate(frames)}
                
                # Processa os resultados à medida que são concluídos
                for future in as_completed(future_to_frame):
                    frame_index = future_to_frame[future]
                    try:
                        processed_frame_path = future.result()
                        processed_frames.append((frame_index, processed_frame_path))
                    except Exception as e:
                        print(f"Erro ao processar o frame {frame_index}: {str(e)}")
                    
                    # Atualiza o progresso
                    if progress_callback and total_frames > 0:
                        progress = (len(processed_frames) / total_frames) * 100
                        elapsed_time = time.time() - start_time
                        remaining_frames = total_frames - len(processed_frames)
                        
                        # Estima o tempo restante
                        if len(processed_frames) > 0 and elapsed_time > 0:
                            time_per_frame = elapsed_time / len(processed_frames)
                            estimated_time_remaining = remaining_frames * time_per_frame
                        else:
                            estimated_time_remaining = 0
                        
                        progress_callback(progress, estimated_time_remaining)
            
            # Ordena os frames processados pelo índice
            processed_frames.sort(key=lambda x: x[0])
            
            # Cria o vídeo de saída
            if processed_frames:
                # Lê o primeiro frame para obter as dimensões
                first_frame = cv2.imread(processed_frames[0][1])
                height, width, _ = first_frame.shape
                
                # Define o codec e cria o objeto VideoWriter
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                # Escreve os frames processados no vídeo de saída
                for _, frame_path in processed_frames:
                    frame = cv2.imread(frame_path)
                    out.write(frame)
                    
                    # Remove o arquivo temporário
                    os.remove(frame_path)
                
                # Libera o vídeo de saída
                out.release()
            
            # Remove a pasta temporária
            try:
                os.rmdir(temp_folder)
            except:
                pass
            
            return True, output_path
        
        except Exception as e:
            return False, f"Erro ao processar o vídeo: {str(e)}"
        
        finally:
            # Garante que os recursos sejam liberados mesmo em caso de erro
            if 'cap' in locals() and cap is not None:
                cap.release()
            if 'out' in locals() and out is not None:
                out.release()
    
    def _process_frame(self, frame, video_path=None, output_folder=None, frame_idx=0):
        """
        Processa um frame detectando pose e desenhando landmarks básicos.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            video_path (str, optional): Caminho do vídeo original (para salvamento de erro)
            output_folder (str, optional): Pasta de saída (para salvamento de erro)
            frame_idx (int): Índice do frame
            
        Returns:
            numpy.ndarray: Frame processado
        """
        try:
            # Redimensiona o frame se necessário
            resize_width = self.config.get('resize_width')
            if resize_width and resize_width > 0 and frame.shape[1] > resize_width:
                scale = resize_width / frame.shape[1]
                frame = cv2.resize(frame, (resize_width, int(frame.shape[0] * scale)))
            
            # Converte BGR para RGB para o MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Processa o frame com MediaPipe
            results = self.pose.process(rgb_frame)
            
            # Desenha os landmarks se detectados
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
                )
            
            return frame
            
        except Exception as e:
            print(f"Erro ao processar frame {frame_idx}: {str(e)}")
            return frame  # Retorna o frame original em caso de erro
    
    def _process_frame_file(self, frame_path):
        """
        Processa um frame salvo em arquivo.
        
        Args:
            frame_path (str): Caminho do arquivo do frame
            
        Returns:
            str: Caminho do arquivo do frame processado
        """
        # Lê o frame
        frame = cv2.imread(frame_path)
        
        # Processa o frame
        processed_frame = self._process_frame(frame, frame_path, os.path.dirname(frame_path), 0)
        
        # Salva o frame processado
        cv2.imwrite(frame_path, processed_frame)
        
        return frame_path
    
    def release(self):
        """
        Libera os recursos do processador.
        """
        if hasattr(self, 'pose') and self.pose:
            self.pose.close()