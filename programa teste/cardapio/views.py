# cardapio/views.py (CÓDIGO COMPLETO PARA SUBSTITUIÇÃO)

from django.shortcuts import render, redirect 
from django.db import transaction, IntegrityError 
from django.contrib import messages 
from .models import Prato, Categoria, Pedido, ItemPedido 


def home_view(request):
    """
    Renderiza a página inicial.
    """
    return render(request, 'home.html')

def cardapio_view(request):
    """
    Renderiza a página do cardápio completo.
    """
    # 1. Busca todas as categorias
    categorias = Categoria.objects.all()
    
    # 2. Cria uma lista de categorias, incluindo os pratos de cada uma
    categorias_com_pratos = []
    
    for categoria in categorias:
        # 3. Busca os pratos de cada categoria
        pratos = Prato.objects.filter(categoria=categoria).order_by('codigo_cardapio')
        
        # 4. Adiciona ao contexto
        categorias_com_pratos.append({
            'nome': categoria.nome,
            'pratos': pratos
        })

    context = {
        'categorias_com_pratos': categorias_com_pratos
    }
    
    return render(request, 'cardapio.html', context)


def fazer_pedido_view(request):
    """
    Renderiza a página para o garçom selecionar os pratos e criar um pedido,
    e processa o envio (POST) do formulário de pedido.
    """
    categorias = Categoria.objects.all()
    categorias_com_pratos = []
    
    # --------------------------------------------------
    # Lógica de processamento do formulário (POST)
    # --------------------------------------------------
    if request.method == 'POST':
        nome_cliente = request.POST.get('nome_cliente')
        itens_do_pedido = []
        
        # 1. Coleta os itens e quantidades do formulário
        for key, value in request.POST.items():
            if key.startswith('quantidade_') and value.isdigit() and int(value) > 0:
                prato_id = key.split('_')[1]
                quantidade = int(value)
                itens_do_pedido.append((prato_id, quantidade))
        
        # Validação
        if not nome_cliente or not itens_do_pedido:
            messages.error(request, "Preencha o nome do cliente/mesa e selecione pelo menos um item.")

        else:
            try:
                # 2. Inicia a Transação (garante que todos os passos sejam executados ou abortados)
                with transaction.atomic():
                    # A. Cria o Pedido (cabeçalho)
                    novo_pedido = Pedido.objects.create(
                        nome_cliente=nome_cliente,
                        pago=False 
                    )
                    
                    # B. Processa cada item do pedido
                    for prato_id, quantidade in itens_do_pedido:
                        # select_for_update bloqueia o prato para evitar erros de estoque simultâneo
                        prato = Prato.objects.select_for_update().get(id=prato_id) 
                        
                        # C. Verifica Estoque 
                        if prato.estoque < quantidade:
                            raise ValueError(f"Estoque insuficiente para {prato.nome}. Disponível: {prato.estoque}")
                        
                        # D. Cria o ItemPedido (detalhe)
                        ItemPedido.objects.create(
                            pedido=novo_pedido,
                            prato=prato,
                            quantidade=quantidade,
                            preco_unitario=prato.preco
                        )
                        
                        # E. Atualiza o Estoque
                        prato.estoque -= quantidade
                        prato.save()

                # Se a transação for bem-sucedida, envia a mensagem de sucesso
                messages.success(request, f"Pedido #{novo_pedido.id} para {nome_cliente} registrado e enviado ao caixa!")
                
                # Redireciona para a mesma página para limpar o formulário
                return redirect('fazer_pedido') 
                
            except ValueError as e:
                # Erros de estoque (lançado pelo raise ValueError)
                messages.error(request, f"ERRO no Pedido: {e}")
                
            except IntegrityError:
                # Erros genéricos de banco de dados
                messages.error(request, "ERRO ao salvar o pedido. Tente novamente.")
            
    # --------------------------------------------------
    # Lógica de Carregamento de Dados (GET)
    # --------------------------------------------------
    for categoria in categorias:
        # Filtra apenas pratos que têm estoque maior que zero para mostrar ao garçom
        pratos = Prato.objects.filter(categoria=categoria, estoque__gt=0).order_by('codigo_cardapio')
        categorias_com_pratos.append({
            'nome': categoria.nome,
            'pratos': pratos
        })

    context = {
        'categorias_com_pratos': categorias_com_pratos
    }
    
    return render(request, 'fazer_pedido.html', context)