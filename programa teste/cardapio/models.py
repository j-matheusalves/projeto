# cardapio/models.py

from django.db import models

# --- MODEL 1: Categoria ---
class Categoria(models.Model):
    """
    Define as categorias de pratos (Ex: 'Entradas', 'Bebidas').
    """
    nome = models.CharField(max_length=100, unique=True)
    
    class Meta:
        # Define o nome da tabela no plural para melhor leitura no Admin
        verbose_name_plural = 'Categorias'
    
    def __str__(self):
        # Retorna o nome da categoria no Admin do Django
        return self.nome

# --- MODEL 2: Prato ---
class Prato(models.Model):
    """
    Define os pratos e bebidas do cardápio.
    """
    # Relação: Um prato pertence a uma Categoria (ForeignKey)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    
    # ID ou Código (Ex: E1, P1, B1) - O Django já cria um ID numérico automático
    codigo_cardapio = models.CharField(max_length=10, unique=True)
    
    nome = models.CharField(max_length=200)
    
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Estoque - O campo que você gerenciava no main.py
    estoque = models.IntegerField(default=0)
    
    class Meta:
        # Garante que o prato seja ordenado por nome por padrão
        ordering = ['nome']
        verbose_name_plural = 'Pratos'
    
    def __str__(self):
        # Retorna o nome e código do prato no Admin
        return f"[{self.codigo_cardapio}] {self.nome}"
# cardapio/models.py (ADICIONAR ESTE CÓDIGO NO FINAL)

# --- MODEL 3: Pedido (O cabeçalho do pedido) ---
class Pedido(models.Model):
    """
    Representa um pedido inteiro, com dados do cliente e status.
    """
    # Define a data/hora exata que o pedido foi feito (automaticamente)
    data_pedido = models.DateTimeField(auto_now_add=True)
    
    # Nome do cliente/mesa (se for um pedido interno)
    nome_cliente = models.CharField(max_length=255)
    
    # Status de pagamento
    pago = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-data_pedido'] # Ordena do mais novo para o mais antigo
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.id} - {self.nome_cliente}"
        
    def calcular_total(self):
        """Calcula a soma do preço de todos os itens neste pedido."""
        # Usa o related_name 'itens' definido no ItemPedido
        total = sum(item.preco_unitario * item.quantidade for item in self.itens.all())
        return total
        
# --- MODEL 4: ItemPedido (Os itens dentro do pedido) ---
class ItemPedido(models.Model):
    """
    Representa um item específico dentro de um pedido (Ex: 2x Bife à Parmegiana).
    """
    # Relação: Muitos itens pertencem a um Pedido (ForeignKey)
    # related_name='itens' permite acessar todos os itens de um pedido: pedido.itens.all()
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    
    # Relação: O item se refere a um Prato específico
    prato = models.ForeignKey(Prato, on_delete=models.PROTECT) # PROTECT impede apagar o prato se houver um pedido
    
    quantidade = models.IntegerField(default=1)
    
    # Preço do prato no momento do pedido (garante que o preço não mude se o admin mudar depois)
    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        verbose_name_plural = 'Itens Pedido'

    def __str__(self):
        return f"{self.quantidade}x {self.prato.nome} no Pedido #{self.pedido.id}"