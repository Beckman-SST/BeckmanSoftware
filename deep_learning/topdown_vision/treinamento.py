import deeplabcut
import os

# Definindo caminhos absolutos baseados na localização atual do script
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.join(DIR_BASE, 'dlc_cotovelo_pulso')
IMAGES_PATH = os.path.join(PROJECT_PATH, 'imagens_exemplo')

# Criando diretórios necessários se não existirem
os.makedirs(PROJECT_PATH, exist_ok=True)
os.makedirs(IMAGES_PATH, exist_ok=True)

# Nome do projeto e do experimentador
NOME_PROJETO = 'CotoveloPulsoProjeto'
NOME_EXPERIMENTADOR = 'BeckmanSoftware'

# Função para verificar se o projeto já existe
def verificar_projeto():
    config_path = os.path.join(PROJECT_PATH, f'config_{NOME_PROJETO}_{NOME_EXPERIMENTADOR}.yaml')
    return os.path.exists(config_path)

# Função para criar um novo projeto DeepLabCut
def criar_projeto():
    print("\n===== CRIANDO NOVO PROJETO DEEPLABCUT =====\n")
    print(f"Projeto: {NOME_PROJETO}")
    print(f"Experimentador: {NOME_EXPERIMENTADOR}")
    print(f"Diretório de trabalho: {PROJECT_PATH}")
    print("\nAtenção: Você precisa adicionar imagens de exemplo na pasta:")
    print(f"{IMAGES_PATH}\n")
    
    # Verificar se existem imagens de exemplo
    imagens = [f for f in os.listdir(IMAGES_PATH) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    if not imagens:
        print("ERRO: Nenhuma imagem encontrada na pasta de exemplos!")
        print("Por favor, adicione pelo menos 1-2 imagens antes de continuar.")
        return False
    
    # Caminhos completos para as imagens
    caminhos_imagens = [os.path.join(IMAGES_PATH, img) for img in imagens]
    
    print(f"Imagens encontradas: {len(imagens)}")
    for img in imagens:
        print(f" - {img}")
    
    # Criar o projeto DeepLabCut
    try:
        deeplabcut.create_new_project(
            NOME_PROJETO,
            NOME_EXPERIMENTADOR,
            caminhos_imagens,
            working_directory=PROJECT_PATH,
            copy_videos=True
        )
        print("\nProjeto criado com sucesso!")
        return True
    except Exception as e:
        print(f"\nErro ao criar projeto: {str(e)}")
        return False

# Função para configurar o projeto
def configurar_projeto():
    config_path = os.path.join(PROJECT_PATH, f'config_{NOME_PROJETO}_{NOME_EXPERIMENTADOR}.yaml')
    
    print("\n===== CONFIGURANDO PROJETO =====\n")
    print("Configurando parâmetros do projeto...")
    
    try:
        # Editar configurações (opcional)
        # deeplabcut.edit_config(config_path, numframes2pick=5)
        
        print("\nPróximos passos:")
        print("1. Extrair frames para rotulagem:")
        print("   deeplabcut.extract_frames(config_path, 'automatic', 'kmeans')")
        print("\n2. Rotular frames (interface gráfica):")
        print("   deeplabcut.label_frames(config_path)")
        print("\n3. Verificar rótulos:")
        print("   deeplabcut.check_labels(config_path)")
        print("\n4. Criar conjunto de treinamento:")
        print("   deeplabcut.create_training_dataset(config_path)")
        print("\n5. Treinar rede:")
        print("   deeplabcut.train_network(config_path)")
        
        return True
    except Exception as e:
        print(f"\nErro ao configurar projeto: {str(e)}")
        return False

# Função principal
def main():
    print("\n===== TREINAMENTO DEEPLABCUT PARA VISÃO TOP-DOWN =====\n")
    print("Este script irá configurar e iniciar o treinamento de um modelo")
    print("DeepLabCut para análise de cotovelo e pulso em visão top-down.")
    
    if verificar_projeto():
        print("\nProjeto existente encontrado!")
        resposta = input("Deseja continuar com a configuração? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        configurar_projeto()
    else:
        print("\nNenhum projeto existente encontrado.")
        resposta = input("Deseja criar um novo projeto? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        
        if criar_projeto():
            configurar_projeto()

# Executar o script
if __name__ == "__main__":
    main()
