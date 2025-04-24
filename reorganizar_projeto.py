import os
import shutil
import sys

def criar_estrutura_pastas():
    """Cria a nova estrutura de pastas para o projeto."""
    pastas = [
        'frontend/static/css',
        'frontend/static/js',
        'frontend/static/images',
        'frontend/templates',
        'backend/models',
        'data/images',
        'data/videos',
    ]
    
    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)
        print(f"✓ Pasta criada: {pasta}")

def mover_arquivo(origem, destino):
    """Move um arquivo de origem para destino, criando diretórios se necessário."""
    try:
        # Criar diretório de destino se não existir
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        
        # Verificar se o arquivo de origem existe
        if not os.path.exists(origem):
            print(f"⚠ Arquivo não encontrado: {origem}")
            return False
        
        # Verificar se já existe um arquivo no destino
        if os.path.exists(destino):
            nome_base, extensao = os.path.splitext(destino)
            destino = f"{nome_base}_old{extensao}"
            print(f"⚠ Arquivo já existe no destino. Salvando como: {destino}")
        
        # Mover o arquivo
        shutil.copy2(origem, destino)
        print(f"✓ Arquivo movido: {origem} → {destino}")
        return True
    except Exception as e:
        print(f"✗ Erro ao mover {origem}: {str(e)}")
        return False

def mover_templates():
    """Move os arquivos HTML para frontend/templates."""
    print("\n== Movendo templates HTML ==")
    arquivos = [
        ('backend/templates/index.html', 'frontend/templates/index.html'),
        ('backend/templates/config.html', 'frontend/templates/config.html'),
        ('backend/templates/logs.html', 'frontend/templates/logs.html'),
        ('backend/templates/frontend_index.html', 'frontend/templates/index_old.html'),
        ('frontend/index.html', 'frontend/templates/frontend_index.html')
    ]
    
    for origem, destino in arquivos:
        mover_arquivo(origem, destino)

def mover_arquivos_estaticos():
    """Consolida arquivos CSS e JS."""
    print("\n== Movendo arquivos estáticos ==")
    arquivos = [
        ('frontend/styles.css', 'frontend/static/css/styles.css'),
        ('static/css/styles.css', 'frontend/static/css/styles_backup.css'),
        ('frontend/script.js', 'frontend/static/js/script.js'),
        ('static/js/script.js', 'frontend/static/js/script_backup.js')
    ]
    
    for origem, destino in arquivos:
        mover_arquivo(origem, destino)

def mover_modelos():
    """Move os modelos ML para backend/models."""
    print("\n== Movendo modelos ML ==")
    arquivos = [
        ('yolov8n.pt', 'backend/models/yolov8n.pt'),
        ('yolov8s-pose.pt', 'backend/models/yolov8s-pose.pt'),
        ('backend/yolov8n.pt', 'backend/models/yolov8n_backup.pt')
    ]
    
    for origem, destino in arquivos:
        mover_arquivo(origem, destino)

def mover_dados_teste():
    """Move dados de teste para a pasta data."""
    print("\n== Movendo dados de teste ==")
    
    # Mover imagens
    if os.path.exists('backend/Imagens'):
        for arquivo in os.listdir('backend/Imagens'):
            origem = os.path.join('backend/Imagens', arquivo)
            destino = os.path.join('data/images', arquivo)
            mover_arquivo(origem, destino)
    
    # Mover vídeos
    if os.path.exists('backend/Videos'):
        for arquivo in os.listdir('backend/Videos'):
            origem = os.path.join('backend/Videos', arquivo)
            destino = os.path.join('data/videos', arquivo)
            mover_arquivo(origem, destino)

def main():
    print("=== REORGANIZAÇÃO DO PROJETO REPOSTURE ===")
    print("Este script irá reorganizar a estrutura de arquivos do projeto.")
    print("ATENÇÃO: Recomenda-se fazer um backup antes de prosseguir.")
    
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() != 's':
        print("Operação cancelada.")
        sys.exit(0)
    
    # Executar as etapas de migração
    criar_estrutura_pastas()
    mover_templates()
    mover_arquivos_estaticos()
    mover_modelos()
    mover_dados_teste()
    
    print("\n=== REORGANIZAÇÃO CONCLUÍDA ===")
    print("Verifique se todos os arquivos foram movidos corretamente.")
    print("Próximos passos:")
    print("1. Atualizar referências nos arquivos HTML")
    print("2. Atualizar caminhos no código Python (app.py e processamento.py)")
    print("3. Testar a aplicação")

if __name__ == "__main__":
    main()