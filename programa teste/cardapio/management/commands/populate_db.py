# cardapio/management/commands/populate_db.py
import os, json
from django.core.management.base import BaseCommand
from django.conf import settings
from cardapio.models import Categoria, Prato

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados do cardapio.json'

    def handle(self, *args, **options):
        # O caminho é relativo a BASE_DIR.parent
        JSON_FILE_PATH = os.path.join(settings.BASE_DIR.parent, 'programa teste', 'cardapio', 'cardapio.json')
        
        # 1. Limpar dados
        self.stdout.write("Limpando dados antigos...")
        Prato.objects.all().delete()
        Categoria.objects.all().delete()

        self.stdout.write(f"Carregando dados de: {JSON_FILE_PATH}")
        try:
            # Tenta carregar o arquivo JSON
            with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"ERRO: Arquivo cardapio.json não encontrado no caminho: {JSON_FILE_PATH}"))
            return

        # 2. Inserir dados
        self.stdout.write("Iniciando inserção de dados...")
        
        prato_count = 0
        for categoria_nome, itens in data.items():
            # Cria ou busca a categoria (entrada no banco)
            categoria_obj, created = Categoria.objects.get_or_create(nome=categoria_nome)
            
            # Insere cada prato/bebida
            for codigo, prato_info in itens.items():
                Prato.objects.create(
                    categoria=categoria_obj,
                    codigo_cardapio=codigo,
                    nome=prato_info['nome'],
                    preco=prato_info['preco'],
                    estoque=prato_info['estoque']
                )
                prato_count += 1
                
        self.stdout.write(self.style.SUCCESS(f"\n✅ Inserção de dados concluída! {prato_count} pratos inseridos."))