# cardapio/admin.py (CÓDIGO CORRIGIDO E COMPLETO)

from django.contrib import admin
from .models import Categoria, Prato, Pedido, ItemPedido

# 1. Configuração para visualizar os itens do pedido dentro do Pedido (Inlines)
class ItemPedidoInline(admin.TabularInline):
    # Faz o link para o modelo ItemPedido
    model = ItemPedido
    # Define os campos que serão exibidos e editáveis
    fields = ['prato', 'quantidade', 'preco_unitario']
    # Define quantos campos vazios devem aparecer para adicionar novos itens
    extra = 1
    # O ItemPedido.preco_unitario deve ser calculado, então o tornamos read-only
    readonly_fields = ['preco_unitario']


# 2. Configuração do Pedido (Header)
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista principal do Pedido
    list_display = ['id', 'nome_cliente', 'data_pedido', 'total_pedido', 'pago']
    # Campos que podem ser usados para buscar pedidos
    search_fields = ['nome_cliente', 'id']
    # Campos que permitem filtrar a lista
    list_filter = ['data_pedido', 'pago']
    # Adiciona os Itens Pedido (Inline) para aparecerem abaixo do cabeçalho do Pedido
    inlines = [ItemPedidoInline]
    
    # Campo total_pedido não existe no modelo, mas será calculado
    readonly_fields = ['total_pedido']

    # Método para calcular o total do pedido na lista
    def total_pedido(self, obj):
        return obj.calcular_total()
    total_pedido.short_description = 'Total (R$)' # Nome da coluna


# 3. Registro dos modelos simples (que você já tinha)
admin.site.register(Categoria)
admin.site.register(Prato)

# OBS: Não precisamos registrar ItemPedido porque ele está dentro do PedidoAdmin