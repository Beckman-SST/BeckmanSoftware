import sys
import signal
from multiprocessing import Pool

# Variável global para controle do processamento
deve_continuar = True

# Handler para sinal de interrupção
def signal_handler(sig, frame):
    global deve_continuar
    deve_continuar = False
    print("\nProcessamento recebeu sinal de cancelamento...")
    sys.exit(0)

# Configuração do handler de sinal
signal.signal(signal.SIGINT, signal_handler)

# Função para processar frames em paralelo
def process_frames_parallel(frames, process_function):
    with Pool() as pool:
        return pool.map(process_function, frames)

# Função para verificar se o processamento deve continuar
def should_continue():
    return deve_continuar