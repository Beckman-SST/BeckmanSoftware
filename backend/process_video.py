from modules.processors.video_processor import VideoProcessor
import os

def main():
    # Inicializa o processador de vídeo
    processor = VideoProcessor()
    
    # Define os caminhos de entrada e saída
    input_folder = os.path.join(os.path.dirname(__file__), 'modules', 'data', 'videos')
    output_folder = os.path.join(os.path.dirname(__file__), 'modules', 'data', 'output')
    
    # Lista todos os vídeos na pasta de entrada
    video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.avi', '.mov'))]
    
    if not video_files:
        print("Nenhum vídeo encontrado na pasta de entrada.")
        return
    
    # Processa cada vídeo encontrado
    for video_file in video_files:
        input_path = os.path.join(input_folder, video_file)
        print(f"\nProcessando vídeo: {video_file}")
        
        # Processa o vídeo e salva o resultado
        output_path = processor.process_video(input_path, output_folder)
        
        if output_path:
            print(f"Processamento concluído com sucesso!")
        else:
            print(f"Erro ao processar o vídeo {video_file}")

if __name__ == "__main__":
    main()