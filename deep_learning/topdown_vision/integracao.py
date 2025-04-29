import os
import sys
import cv2
import numpy as np

# Adicionar o diretório pai ao path para importar módulos do sistema principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar DeepLabCut
try:
    import deeplabcut
    print("DeepLabCut importado com sucesso!")
except ImportError:
    print("ERRO: DeepLabCut não está instalado. Execute 'pip install deeplabcut' para instalá-lo.")
    sys.exit(1)

# Configurações do projeto
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.join(DIR_BASE, 'dlc_cotovelo_pulso')
NOME_PROJETO = 'CotoveloPulsoProjeto'
NOME_EXPERIMENTADOR = 'BeckmanSoftware'
CONFIG_PATH = os.path.join(PROJECT_PATH, f'config_{NOME_PROJETO}_{NOME_EXPERIMENTADOR}.yaml')

# Verificar se o projeto existe
def verificar_projeto():
    if not os.path.exists(CONFIG_PATH):
        print(f"ERRO: Projeto DeepLabCut não encontrado em {CONFIG_PATH}")
        print("Execute primeiro o script treinamento.py para criar e treinar o modelo.")
        return False
    return True

# Classe para integração com o sistema principal
class DeepLabCutIntegrador:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        
        # Verificar se o modelo foi treinado
        if not self.verificar_modelo_treinado():
            print("AVISO: Modelo não encontrado ou não treinado completamente.")
            print("Execute o fluxo completo de treinamento antes de usar este integrador.")
        
        # Carregar o modelo para análise
        try:
            print("Carregando modelo DeepLabCut...")
            self.dlc = deeplabcut
            # Inicializar o modelo para análise de vídeo/imagem
            # Nota: O modelo será carregado na primeira chamada de análise
        except Exception as e:
            print(f"ERRO ao carregar modelo: {str(e)}")
    
    def verificar_modelo_treinado(self):
        # Verificar se o diretório dlc-models existe (criado após treinamento)
        models_dir = os.path.join(os.path.dirname(self.config_path), 'dlc-models')
        return os.path.exists(models_dir)
    
    def analisar_imagem(self, imagem):
        """Analisa uma única imagem e retorna as coordenadas dos pontos-chave."""
        if isinstance(imagem, str):
            # Se for um caminho de arquivo
            if not os.path.exists(imagem):
                print(f"ERRO: Imagem não encontrada: {imagem}")
                return None
        
        try:
            # Salvar imagem temporária se for um array numpy
            temp_img_path = None
            if not isinstance(imagem, str):
                temp_img_path = os.path.join(PROJECT_PATH, 'temp_analysis.png')
                cv2.imwrite(temp_img_path, imagem)
                imagem = temp_img_path
            
            # Analisar a imagem com DeepLabCut
            resultados = self.dlc.analyze_time.analyze_time(
                self.config_path,
                [imagem],
                videotype='image',
                save_as_csv=False
            )
            
            # Carregar os resultados
            dados = self.dlc.analyze_time.read_pickle(resultados[0])
            
            # Limpar arquivo temporário
            if temp_img_path and os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            
            return self.processar_resultados(dados)
            
        except Exception as e:
            print(f"ERRO durante análise da imagem: {str(e)}")
            return None
    
    def processar_resultados(self, dados):
        """Processa os resultados brutos do DeepLabCut para um formato utilizável."""
        try:
            # Extrair coordenadas dos pontos-chave
            # A estrutura exata depende da configuração do seu projeto
            resultados_processados = {
                'cotovelo_direito': None,
                'pulso_direito': None,
                'cotovelo_esquerdo': None,
                'pulso_esquerdo': None,
                'confianca': {}
            }
            
            # Exemplo de extração (ajuste conforme seus pontos-chave específicos)
            for parte, coords in dados.items():
                if 'cotovelo' in parte.lower():
                    lado = 'direito' if 'direito' in parte.lower() else 'esquerdo'
                    resultados_processados[f'cotovelo_{lado}'] = (int(coords[0]), int(coords[1]))
                    resultados_processados['confianca'][f'cotovelo_{lado}'] = float(coords[2])
                
                elif 'pulso' in parte.lower():
                    lado = 'direito' if 'direito' in parte.lower() else 'esquerdo'
                    resultados_processados[f'pulso_{lado}'] = (int(coords[0]), int(coords[1]))
                    resultados_processados['confianca'][f'pulso_{lado}'] = float(coords[2])
            
            return resultados_processados
            
        except Exception as e:
            print(f"ERRO ao processar resultados: {str(e)}")
            return None
    
    def calcular_angulo_cotovelo(self, ombro, cotovelo, pulso):
        """Calcula o ângulo do cotovelo a partir das coordenadas."""
        if None in [ombro, cotovelo, pulso]:
            return None
        
        try:
            # Converter para arrays numpy
            a = np.array(ombro)
            b = np.array(cotovelo)
            c = np.array(pulso)
            
            # Calcular vetores
            ba = a - b
            bc = c - b
            
            # Calcular ângulo
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            # Converter para graus
            return np.degrees(angle)
            
        except Exception as e:
            print(f"ERRO ao calcular ângulo: {str(e)}")
            return None

# Função para demonstração
def demonstracao():
    if not verificar_projeto():
        return
    
    print("\n===== DEMONSTRAÇÃO DE INTEGRAÇÃO DEEPLABCUT =====\n")
    
    # Criar instância do integrador
    integrador = DeepLabCutIntegrador()
    
    # Solicitar caminho da imagem para teste
    imagem_path = input("Digite o caminho para uma imagem de teste (ou pressione Enter para sair): ")
    if not imagem_path:
        return
    
    if not os.path.exists(imagem_path):
        print(f"ERRO: Arquivo não encontrado: {imagem_path}")
        return
    
    # Analisar a imagem
    print(f"\nAnalisando imagem: {imagem_path}")
    resultados = integrador.analisar_imagem(imagem_path)
    
    if resultados:
        print("\nResultados da análise:")
        for parte, coords in resultados.items():
            if parte != 'confianca':
                print(f"{parte}: {coords}")
        
        print("\nNíveis de confiança:")
        for parte, conf in resultados['confianca'].items():
            print(f"{parte}: {conf:.2f}")
    else:
        print("Não foi possível analisar a imagem.")

# Função principal
def main():
    print("\n===== INTEGRAÇÃO DEEPLABCUT PARA VISÃO TOP-DOWN =====\n")
    print("Este script permite integrar o modelo DeepLabCut treinado")
    print("ao sistema principal para análise de cotovelo e pulso.")
    
    if not verificar_projeto():
        print("\nCrie e treine o modelo primeiro usando o script treinamento.py")
        return
    
    # Menu de opções
    while True:
        print("\nOpções:")
        print("1. Executar demonstração")
        print("2. Verificar status do modelo")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '1':
            demonstracao()
        elif opcao == '2':
            integrador = DeepLabCutIntegrador()
            status = "Treinado e pronto" if integrador.verificar_modelo_treinado() else "Não treinado"
            print(f"\nStatus do modelo: {status}")
        elif opcao == '0':
            break
        else:
            print("Opção inválida!")

# Executar o script
if __name__ == "__main__":
    main()