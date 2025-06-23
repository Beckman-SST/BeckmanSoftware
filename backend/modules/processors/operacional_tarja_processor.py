import cv2
import os
from ..core.utils import ensure_directory_exists, resize_frame
from ..detection.pose_detector import PoseDetector
from ..visualization.video_visualizer import VideoVisualizer

class OperacionalTarjaProcessor:
    def __init__(self, config):
        self.config = config
        self.pose_detector = PoseDetector(
            min_detection_confidence=config.get('min_detection_confidence', 0.8),
            min_tracking_confidence=config.get('min_tracking_confidence', 0.8),
            moving_average_window=config.get('moving_average_window', 5)
        )
        self.visualizer = VideoVisualizer()

    def process_image(self, image_path, output_folder):
        if not os.path.exists(image_path):
            return False, f"Arquivo não encontrado: {image_path}"
        ensure_directory_exists(output_folder)
        frame = cv2.imread(image_path)
        if frame is None:
            return False, f"Não foi possível carregar a imagem: {image_path}"
        resize_width = self.config.get('resize_width')
        if resize_width and resize_width > 0:
            frame = resize_frame(frame, resize_width)
        frame_rgb, results = self.pose_detector.detect(frame)
        height, width, _ = frame.shape
        face_landmarks = self.pose_detector.get_face_landmarks(results, width, height)
        processed_frame = self.visualizer.apply_face_blur(frame, face_landmarks)
        output_filename = os.path.basename(image_path)
        output_path = os.path.join(output_folder, output_filename)
        cv2.imwrite(output_path, processed_frame)
        return True, output_path