# cardapio/urls.py

from django.urls import path
from . import views

# Define as rotas (URLs) do aplicativo 'cardapio'
urlpatterns = [
    # Rota principal (/)
    path('', views.home_view, name='home'), 
    
    # Rota do cardápio para o cliente
    path('menu/', views.cardapio_view, name='cardapio'),
    
    # ROTA CORRIGIDA PARA O GARÇOM (resolve o NoReverseMatch)
    path('fazer_pedido/', views.fazer_pedido_view, name='fazer_pedido'), 
]