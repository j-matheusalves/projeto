# cardapio/populate_data.py

import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from .models import Categoria, Prato

# Define o caminho para o arquivo JSON (dentro da pasta 'cardapio')
JSON_FILE_PATH = os.path.join(settings.BASE_DIR.parent, 'cardapio', 'cardapio.json')

def load_data():
    """Lê o JSON, limpa dados antigos e insere novos dados no banco."""
    
    # 1. Limpa dados antigos para evitar duplicatas
    print("Limpando dados antigos...")
    Prato.objects.all().delete()
    Categoria.objects.all().delete()
    
    # 2. Abre e carrega os dados do cardapio.json
    print(f"Carregando dados de: {JSON_FILE_PATH}")
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERRO: Arquivo cardapio.json não encontrado no caminho esperado: {JSON_FILE_PATH}")
        return

    # 3. Insere os dados
    print("Iniciando inserção de dados...")
    
    for categoria_nome, itens in data.items():
        # Cria a Categoria (Ex: 'Entradas')
        categoria_obj, created = Categoria.objects.get_or_create(nome=categoria_nome)
        
        if created:
            print(f"  > Categoria '{categoria_nome}' criada.")
        else:
            print(f"  > Categoria '{categoria_nome}' já existia.")
            
        for codigo, prato_info in itens.items():
            # Cria o Prato
            Prato.objects.create(
                categoria=categoria_obj,
                codigo_cardapio=codigo,
                nome=prato_info['nome'],
                preco=prato_info['preco'],
                estoque=prato_info['estoque']
            )
            
    print("\n✅ Inserção de dados concluída com sucesso!")


# Esta parte é necessária para o script rodar corretamente
if __name__ == '__main__':
    # Configura o ambiente Django para que os models funcionem
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Restaurante_Site.settings')
    import django
    django.setup()
    
    load_data()